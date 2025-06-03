from django.views import generic, View

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db.models import Q

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
User = get_user_model()

from django.utils import timezone

from datetime import datetime, date

from forms.forms import RespondentForm
from forms.models import Respondent, Response

class ViewRespondentsIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/respondents/view-respondents-index.html'
    context_object_name = 'respondents'
    def get_queryset(self):
        user = self.request.user
        if user.userprofile.access_level == 'admin':
            return Respondent.objects.all()
        else:
            return Respondent.objects.filter(
                Q(created_by=user) |
                Q(created_by__userprofile__manager=user) |
                Q(created_by__userprofile__supervisor=user)
            )

class ViewRespondentDetail(LoginRequiredMixin, generic.DetailView):
    model=Respondent
    template_name = 'forms/respondents/view-respondent-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        respondent = self.get_object()
        responses = Response.objects.filter(respondent=respondent).order_by('response_date')
        context['respondent'] = respondent
        context['responses'] = responses
        context['user_org'] = user_org
        return context


class CreateRespondent(LoginRequiredMixin, generic.CreateView):
    model = Respondent
    template_name = 'forms/respondents/update-respondent.html'
    form_class = RespondentForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('forms:view-respondent-detail', kwargs={'pk': self.object.id})


class UpdateRespondent(LoginRequiredMixin, generic.UpdateView):
    model=Respondent
    template_name = 'forms/respondents/update-respondent.html'
    form_class = RespondentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('forms:view-respondent-detail', kwargs={'pk': self.object.id})
   

class DeleteRespondent(LoginRequiredMixin, generic.DeleteView):
    model=Respondent
    success_url = reverse_lazy('forms:view-respondents-index')