from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

User = get_user_model()

class Home(LoginRequiredMixin, View):
    def get(self, request):
        user = self.request.user
        userProfile = user.userprofile
        return render(request, 'home/home.html', {'user':user, 'userProfile':userProfile})
