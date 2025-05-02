from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils import timezone
from django.db.models import Count

from datetime import datetime, date

class Organization(models.Model):
    organization_name = models.CharField(max_length=255, verbose_name='Organization Name')
    parent_organization = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Parent Organization')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization_name

class UserProfile(models.Model):
    DC = 'data-collector'
    SUP = 'supervisor'
    MGR = 'manager'
    ADM = 'admin'
    ACCESS_LEVEL_CHOICES = [
        (DC,'Data Collector'), 
        (SUP,'Supervisor'), 
        (MGR,'Manager'),
        (ADM, 'Administrator')
        ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervisor')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='manager')
    access_level = models.CharField(max_length=100, choices=ACCESS_LEVEL_CHOICES, default=DC)

'''
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        default_org = Organization.objects.filter(organization_name='Unassigned').first()
        UserProfile.objects.create(user=instance, organization=default_org)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
'''

class Respondent(models.Model):
    F = 'F'
    M = 'M'
    NB = 'NB'
    SEX_CHOICES = [
        (M,'Male'), 
        (F,'Female'), 
        (NB,'Non-Binary')
        ]
    id_no = models.CharField(max_length=255, unique=True, verbose_name='ID/Passport Number')
    fname = models.CharField(max_length=255, verbose_name='First Name')
    lname = models.CharField(max_length=255, verbose_name='Last Name')
    dob = models.DateField(verbose_name='Date of Birth')
    sex = models.CharField(max_length=2, choices=SEX_CHOICES, default=NB, verbose_name='Sex')
    ward = models.CharField(max_length=255, verbose_name='Ward')
    village = models.CharField(max_length=255, verbose_name='Village')
    district = models.CharField(max_length=255, verbose_name='District')
    citizenship = models.CharField(max_length=255, verbose_name='Citizenship/Nationality')
    email = models.EmailField(verbose_name='Email Address', null=True, blank=True)
    contact_no = models.CharField(max_length=255, verbose_name='Phone Number', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, default=User.objects.first().id, on_delete=models.SET_DEFAULT)

    def get_full_name(self):
        return f'{self.fname} {self.lname}'
    
    def get_age(self):
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
    def responsesCount(self):
        return Response.objects.filter(respondent_id=self.id).count()
    
    def __str__(self):
        return self.get_full_name()
    
    class Meta:
        db_table_comment = 'Basic information about respondents/clients.'
        ordering = ['lname', 'fname']

class Form(models.Model):
    form_name = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField('Start Date')
    end_date = models.DateField('End Date')
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, default=User.objects.first().id, on_delete=models.SET_DEFAULT)
    def __str__(self):
        return f'{self.organization}: {self.form_name}'
    
    def isActive(self):
        return date.today() >= self.end_date
    
    def responsesCount(self):
        return Response.objects.filter(form_id=self.id).count()

    class Meta:
        db_table_comment = 'Table containing "forms" which consist of a series of "questions" a respondent was asked.'
        ordering = ['-created_date', 'form_name']

class Question(models.Model):
    TEXT = 'Text'
    BINARY = 'Yes/No'
    NUMBER = 'Number'
    SINGLE_SELECT = 'Single Selection'
    MULTI_SELECT = 'Multiple Selections'

    QTYPE_CHOICES = [
        (TEXT, 'Text'),
        (BINARY, 'Yes/No'),
        (NUMBER, 'Number'),
        (SINGLE_SELECT, 'Single Selection'),
        (MULTI_SELECT, 'Multiple Selections'),
    ]
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QTYPE_CHOICES, default=TEXT)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text
    
    def created_recently(self):
        return  timezone.now() - datetime.timedelta(days=1) <= self.created_date <= timezone.now()
    
    def options(self):
        return self.option_set.count()
    
    class Meta:
        db_table_comment = 'Table containing questions that a respondent may be asked. This may include questions about services provided to a client.'
        ordering = ['question_text']

class FormQuestion(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='questions')
    visible_if_question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.SET_NULL, related_name='question_logic')
    visible_if_answer = models.TextField(null=True, blank=True)
    index = models.IntegerField()
    def __str__(self):
        return f'Question: {self.question} located in form {self.form}.'
    
    class Meta:
        db_table_comment = 'Table containing a list of questions asked in a particular form.'
        ordering = ['form', 'question']
        #unique_together = ['form', 'question']

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_text = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.option_text

    def responses(self):
        return self.response_set.count()
    
    class Meta:
        db_table_comment = 'Table with options associated with a particular question.'
        ordering = ['question', 'option_text']
    
class Response(models.Model):
    respondent = models.ForeignKey(Respondent, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, default=User.objects.first().id, on_delete=models.SET_DEFAULT)
    response_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Response from {self.respondent.get_full_name()} for {self.form} given on date {str(self.response_date)}'
    
    class Meta:
        db_table_comment = 'Table containing responses, or an instance of a respondent completing a survey.'
        ordering = ['-response_date', 'form', 'respondent']
        #unique_together = ['form', 'respondent']

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE, blank=True, null=True)
    open_answer = models.TextField(blank=True, null=True)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)

    def __str__(self):
        if self.option != None:
            val = self.option
        else: val = self.open_answer
        return f'{val}'
    
    class Meta:
        db_table_comment = 'Table containing the actual answers to questions a respondent gave.'
        ordering = ['response', 'question', 'option']