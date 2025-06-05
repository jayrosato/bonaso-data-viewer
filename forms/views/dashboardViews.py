from django.views import View
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
User = get_user_model()
from accounts.models import UserProfile

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy


from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, date


from forms.models import Respondent, Form, FormQuestion, Question, Option, Response, Answer, FormLogic, FormLogicRule

#this may eventually get spun off into its own app.
class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'forms/dashboard-creator.html')


#these are 'APIs' that send information specific for creating charts
class GetQuestionData(LoginRequiredMixin, View):
    def get(self, request, pk):
        question = Question.objects.filter(id=pk).first()
        options_count = Option.objects.filter(question=question.id).annotate(num_answers=Count('answer')).order_by('num_answers')
        labels = [option.option_text for option in options_count]
        values = [answer.num_answers for answer in options_count]
        if not options_count:
            options_count = Answer.objects.filter(question=question.id).values('open_answer').annotate(count=Count('open_answer')).order_by('-count')
            labels = [item['open_answer'] for item in options_count]
            values = [item['count'] for item in options_count]
        data = {
            "labels": labels,
            "datasets": [{
                "label": "Options",
                "data": values,
                'backgroundColor': "#FFFFFF",
                'scaleFontColor': '#FFFFFF',
            },]

        }
        return JsonResponse(data) 

class GetData(LoginRequiredMixin, View):
    def get(self, request):
        responses_agg = Form.objects.annotate(num_responses=Count('response')).order_by('-num_responses')
        data = {
            "labels": [form.form_name for form in responses_agg],
            "datasets": [{
                "label": "Responses",
                "data": [form.num_responses for form in responses_agg],
                'backgroundColor': "#FFFFFF",
                'scaleFontColor': '#FFFFFF',
            }]
        }
        return JsonResponse(data)