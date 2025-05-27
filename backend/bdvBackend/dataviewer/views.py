from django.shortcuts import render
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.models import UserProfile

class CreateChart(LoginRequiredMixin, View):
    def get(self, request):
        userProfile = self.request.user.userprofile
        return render(request, 'dataviewer/create-chart.html')

