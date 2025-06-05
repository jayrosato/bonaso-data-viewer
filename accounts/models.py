from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

from organizations.models import Organization

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
    organization = models.ForeignKey('organizations.Organization', on_delete=models.SET_NULL, null=True, blank=True, default=Organization.get_default_pk)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervisor')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='manager')
    access_level = models.CharField(max_length=100, choices=ACCESS_LEVEL_CHOICES, default=DC)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient')
    subject = models.CharField('Subject', max_length=255)
    body = models.TextField('Message Body')
    read = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    sent_on = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Response to')

    def __str__(self):
        return f'{self.subject} from {self.sender} on {self.sent_on.date()}'