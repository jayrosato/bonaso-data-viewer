from django.views import generic, View

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
User = get_user_model()

from django.utils import timezone

from django.http import JsonResponse
import json
from datetime import datetime, date

from forms.forms import QuestionForm
from forms.models import Question, Option


#questions are meant to be modular, and as such are edited separately from forms
class ViewQuestions(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/questions/view-questions.html'
    context_object_name = 'questions'
    
    def get_queryset(self):
        return Question.objects.all()
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        options = Option.objects.all()
        context['options'] = options
        return context

class CreateQuestion(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'forms/questions/create-question.html', 
                          { 'form': QuestionForm(),
                           'msg':'Double check that all the fields are correctly filled out.' })

    def post(self, request):
        try:
            data = json.loads(request.body)
            question = Question(question_text=data.get('question_text'), question_type=data.get('question_type'))
            question.save()
            options = data.get('options')
            if len(options) > 0:
                for i in range(len(options)):
                    special = options[i]['special']
                    if special == '':
                        os = None
                    else:
                        os = options[i]['special']
                    option = Option(question = question, option_text=options[i]['text'], special=os)
                    option.save()
            return JsonResponse({'redirect': reverse('forms:view-questions')})
        except:
            print('Ah nuts')

class UpdateQuestion(LoginRequiredMixin, View):
    def get(self, request, pk):
        question = get_object_or_404(Question, id=pk)
        options = Option.objects.filter(question=question.id)
        return render(request, 'forms/questions/update-question.html', 
                          { 'form': QuestionForm(instance=question), 'options': options,
                           'msg':'Double check that all the fields are correctly filled out.',
                            'question':question })

    def post(self, request, pk):
        try:
            data = json.loads(request.body)
            question = get_object_or_404(Question, id=pk)
            question.question_text = data.get('question_text')
            question.question_type = data.get('question_type')
            question.save()
            options = data.get('options')
            print(options)
            existingOptions = Option.objects.filter(question=question.id)
            if len(existingOptions) > len(options):
                for extra in existingOptions[len(options):]:
                    extra.delete()
            if len(options) > 0:
                for i in range(len(options)):
                    special = options[i]['special']
                    if special == '':
                        os = None
                    else:
                        os = options[i]['special']
                    if i+1 <= len(existingOptions):
                        option = existingOptions[i]
                        option.option_text = options[i]['text']
                        option.special = os
                        option.save()
                    else:
                        option = Option(question = question, option_text=options[i]['text'], special=os)
                        option.save()
            return JsonResponse({'redirect': reverse('forms:view-questions')})
        except:
            print('Ah nuts')


class DeleteQuestion(LoginRequiredMixin, generic.DeleteView):
    model=Question
    def get_success_url(self):
        return reverse_lazy('forms:view-questions')