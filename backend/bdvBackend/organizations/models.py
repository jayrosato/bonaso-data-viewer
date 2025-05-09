from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Count

from datetime import datetime, date

class Organization(models.Model):
    organization_name = models.CharField(max_length=255, verbose_name='Organization Name')
    parent_organization = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Parent Organization')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_default_pk(cls):
        organization, created = cls.objects.get_or_create(
            organization_name='Unassigned'
        )
        return organization.pk

    def __str__(self):
        return self.organization_name

class Target(models.Model):
    question = models.ForeignKey('forms.Question', on_delete=models.CASCADE, related_name='target_question')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, default=Organization.get_default_pk)
    target_amount = models.IntegerField(blank=True, null=True)
    target_start = models.DateField('Target Period Start')
    target_end = models.DateField('Target Period End')
    match_option = models.ForeignKey('forms.Option', blank=True, null=True, default = None, on_delete=models.CASCADE)
    percentage_of_question = models.ForeignKey('forms.Question', on_delete=models.CASCADE, related_name='percent_of_question', blank=True, null=True)
    as_percentage = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return f'Target for {self.organization} for {self.question} for period {self.target_start} to {self.target_end}.'

    def clean(self):
        super().clean()
        if not (self.target_amount or self.percentage_of_question):
            raise ValidationError({
                'target_amount': "Either Target Amount or Percentage of Question must be filled.",
                'percentage_of_question': "Either Target Amount or Percentage of Question must be filled.",
            })
        if(self.percentage_of_question and not self.as_percentage):
            self.as_percentage = 100

    def save(self, *args, **kwargs):
        if self.percentage_of_question and not self.as_percentage:
            self.as_percentage = 100
        self.full_clean()
        super().save(*args, **kwargs)

    def get_actual(self):
        from forms.models import Response, Answer
        responses =  Response.objects.filter(form__organization__id = self.organization.id, response_date__lte= self.target_end, response_date__gte = self.target_start)
        answers = Answer.objects.filter(response__id__in=responses, question=self.question)
        if self.question.question_type == 'Yes/No':
            answers = Answer.objects.filter(response__id__in=responses, question=self.question, open_answer='Yes')
        elif self.question.question_type == 'Single Select' or self.question.question_type == 'Multiple Selections':
            if self.match_option:
                answers = Answer.objects.filter(response__id__in=responses, question=self.question, option=self.match_option)
            else:
                answers = Answer.objects.filter(response__id__in=responses, question=self.question)
        if self.target_amount:
            return answers.values('response').distinct().count()
        else:
            target_count = answers.values('response').distinct().count()
            if self.percentage_of_question.question_type == 'Yes/No':
                ref_answers = Answer.objects.filter(response__id__in=responses, question=self.percentage_of_question, open_answer='Yes')
            elif self.percentage_of_question.question_type == 'Single Select' or self.question.question_type == 'Multiple Selections':
                if self.match_option:
                    ref_answers = Answer.objects.filter(response__id__in=responses, question=self.percentage_of_question, option=self.match_option)
                else:
                    ref_answers = Answer.objects.filter(response__id__in=responses, question=self.percentage_of_question)
            ref_count = ref_answers.values('response').distinct().count()
            if ref_count > 0:
                percentage = f'{(target_count/ref_count)*100}%'
                return percentage
            else:
                return 0
