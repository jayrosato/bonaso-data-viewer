from django.db import models
from django.utils import timezone

import datetime

class Organization(models.Model):
    organization_name = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization_name

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
    email = models.EmailField(verbose_name='Email Address')
    contact_no = models.CharField(max_length=255, verbose_name='Phone Number')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_full_name(self):
        return f'{self.fname} {self.lname}'
    
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

    def __str__(self):
        return f'{self.organization}: {self.form_name}'
    
    def isActive(self):
        return datetime.date.today() >= self.end_date
    
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
    response_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Response from {self.respondent.get_full_name()} for {self.form} given on date {str(self.response_date)}'
    
    class Meta:
        db_table_comment = 'Table containing responses, or an instance of a respondent completing a survey.'
        ordering = ['-response_date', 'form', 'respondent']

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