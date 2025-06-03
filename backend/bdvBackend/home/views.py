from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from django.db.models import Q
from datetime import datetime, date


User = get_user_model()

class Home(LoginRequiredMixin, View):
    def get(self, request):
        from forms.models import Form, Response, Respondent
        from accounts.models import Message
        user = self.request.user
        userProfile = user.userprofile
        today = date.today()
        forms = Form.objects.filter(organization = userProfile.organization, start_date__lte = today, end_date__gte = today)
        responses = Response.objects.filter(created_by=user)
        respondents = Respondent.objects.filter(created_by=user)
        messages = Message.objects.filter(
            Q(recipient=user, parent__isnull=True, completed=False) | 
            Q(recipient=user, parent__isnull=False, read=False)
        )
        return render(request, 'home/home.html', {'user':user, 'userProfile':userProfile, 
                        'forms': forms, 'responses':responses, 'respondents':respondents,
                        'messages':messages})
