from django.db import models
from django.utils import timezone
import datetime

class Question(models.Model):
    question_text = models.CharField(max_length=255)
    created_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question_text
    
    def created_recently(self):
        return  timezone.now() - datetime.timedelta(days=1) <= self.created_date <= timezone.now()

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)
    def __str__(self):
        return self.option_text

    def responses(self):
        return self.response_set.count()
    
class Response(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    response_date = models.DateTimeField('date published')