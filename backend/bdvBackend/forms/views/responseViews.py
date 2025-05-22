from django.views import generic, View
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
User = get_user_model()
from accounts.models import UserProfile

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy


from django.utils import timezone
from django.http import JsonResponse
import json
from datetime import datetime, date

from forms.forms import ResponseForm
from forms.models import Respondent, Form, FormQuestion, Option, Response, Answer


now = timezone.now()

class ViewResponseIndex(LoginRequiredMixin, generic.ListView):
    model=Response
    template_name='forms/responses/view-responses-index.html'
    context_object_name = 'responses'

    def get_queryset(self):
        return Response.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        return context

class ViewResponseDetail(LoginRequiredMixin, generic.DetailView):
    model=Response
    template_name = 'forms/responses/view-response-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response = self.get_object()
        form = Form.objects.filter(id = response.form.id).first()
        formQs = FormQuestion.objects.filter(form = form.id).order_by('index')
        form_questions = [fq.question for fq in formQs]
        answers = []
        for i in range(len(form_questions)):  
            answer = Answer.objects.filter(response=response, question=form_questions[i])
            if answer:
                answers.append([answer for answer in answer])
            else: 
                answers.append('No response given.')
        context['response'] = response
        context['question_answer_pairs'] = zip(form_questions, answers)
        context['form_meta'] = form
        return context
    
class NewResponse(LoginRequiredMixin, View):
    def get(self, request, pk):
        self.form_meta = get_object_or_404(Form, id=pk)
        self.form_structure = FormQuestion.objects.filter(form=self.form_meta).order_by('index')
        self.form_questions = [fq.question for fq in self.form_structure]
        fqIDs = [fq.id for fq in self.form_structure]
        user_org = self.request.user.userprofile.organization
        return render(request, 'forms/responses/create-response.html', 
                    { 'form': ResponseForm(formQs=self.form_questions, fqIDs = fqIDs),
                     'user_org':user_org,
                    'form_meta': self.form_meta,})

    def post(self, request, pk):
        self.form_meta = get_object_or_404(Form, id=pk)
        self.form_structure = FormQuestion.objects.filter(form=self.form_meta).order_by('index')
        self.form_questions = [fq.question for fq in self.form_structure]
        fqIDs = [fq.id for fq in self.form_structure]
        self.form = ResponseForm(request.POST, formQs=self.form_questions, fqIDs = fqIDs)

        #if self.form.is_valid():
        respondent_id = request.POST.get('Respondent')
        response = Response(form=self.form_meta, respondent=get_object_or_404(Respondent, pk=respondent_id), created_by=request.user)
        
        response.save()
        for i in range(len(self.form_questions)):
            if self.form_questions[i].question_type == 'Text' or self.form_questions[i].question_type == 'Number':
                openResponse = request.POST.get(self.form_questions[i].question_text)
                answer = Answer(response=response, question=self.form_questions[i], open_answer=openResponse, option=None)
                answer.save()
            if self.form_questions[i].question_type == 'Yes/No':
                yesNo = request.POST.get(self.form_questions[i].question_text)
                answer = Answer(response=response, question=self.form_questions[i], open_answer=yesNo)
                answer.save()
            if self.form_questions[i].question_type == 'Single Selection':
                option_id = request.POST.get(self.form_questions[i].question_text)
                answer = Answer(response=response, question=self.form_questions[i], option=get_object_or_404(Option, pk=option_id), open_answer=None)
                answer.save()
            if self.form_questions[i].question_type == 'Multiple Selections':
                selected_options = request.POST.getlist(self.form_questions[i].question_text)
                #check if the options selected is none, and if so record nothing
                for o in range(len(selected_options)):
                    option=get_object_or_404(Option, pk=selected_options[o])
                    if option.special == 'None of the above':
                        continue
                    elif option.special == 'All':
                        options = Option.objects.filter(question = self.form_questions[i])
                        for option in options:
                            if not option.special:
                                answer = Answer(response=response, question=self.form_questions[i],  option=option, open_answer=None)
                                answer.save()
                        continue
                    answer = Answer(response=response, question=self.form_questions[i],  option=get_object_or_404(Option, pk=selected_options[o]), open_answer=None)
                    answer.save()
        return HttpResponseRedirect(reverse("forms:view-forms-index"))
        '''
        else:
            print(self.form.errors.items())
            return render(request, 'forms/responses/create-response.html', 
                          { 'form': ResponseForm(request.POST, formQs=self.form_questions), 
                           'form_meta':self.form_meta, 
                           'msg':'Double check that all the fields are correctly filled out.' })
        '''

class UpdateResponse(LoginRequiredMixin, View):
    def get(self, request, pk):
        self.response = get_object_or_404(Response, id=pk)
        self.form_meta = Form.objects.filter(id=self.response.form.id).first()
        self.form_structure = FormQuestion.objects.filter(form=self.form_meta).order_by('index')
        self.form_questions = [fq.question for fq in self.form_structure]
        user_org = self.request.user.userprofile.organization
        return render(request, 'forms/responses/update-response.html', 
                    { 'form': ResponseForm(formQs=self.form_questions, response=self.response),
                     'user':self.request.user, 'user_org':user_org,
                    'form_meta': self.form_meta,
                    'response': self.response})


    def post(self, request, pk):
        self.response = get_object_or_404(Response, id=pk)
        self.form_meta = Form.objects.filter(id=self.response.form.id).first()
        self.form_structure = FormQuestion.objects.filter(form=self.form_meta).order_by('index')
        self.form_questions = [fq.question for fq in self.form_structure]
        self.form = ResponseForm(request.POST, formQs=self.form_questions, response=self.response)


        #if self.form.is_valid():
        self.response.updated_at = timezone.now()
        self.response.save()

        for i in range(len(self.form_questions)):
            if self.form_questions[i].question_type == 'Text' or self.form_questions[i].question_type == 'Number':
                openResponse = request.POST.get(self.form_questions[i].question_text)
                answer = Answer.objects.filter(response = self.response, question=self.form_questions[i]).first()
                answer.open_answer = openResponse
                answer.save()
            if self.form_questions[i].question_type == 'Yes/No':
                yesNo = request.POST.get(self.form_questions[i].question_text)
                answer = Answer.objects.filter(response = self.response, question=self.form_questions[i]).first()
                answer.open_answer = yesNo
                answer.save()
            if self.form_questions[i].question_type == 'Single Selection':
                option_id = request.POST.get(self.form_questions[i].question_text)
                answer = Answer.objects.filter(response = self.response, question=self.form_questions[i]).first()
                answer.option = get_object_or_404(Option, pk=option_id)
                answer.save()
            if self.form_questions[i].question_type == 'Multiple Selections':
                selected_options = request.POST.getlist(self.form_questions[i].question_text)
                previous_answers =  Answer.objects.filter(response = self.response, question=self.form_questions[i])
                for answer in previous_answers:
                    answer.delete()
                for o in range(len(selected_options)):
                    option=get_object_or_404(Option, pk=selected_options[o])
                    if option.special == 'None of the above':
                        continue
                    elif option.special == 'All':
                        options = Option.objects.filter(question = self.form_questions[i])
                        for option in options:
                            if not option.special:
                                answer = Answer(response=self.response, question=self.form_questions[i],  option=option, open_answer=None)
                                answer.save()
                        continue
                    answer = Answer(response=self.response, question=self.form_questions[i],  option=get_object_or_404(Option, pk=selected_options[o]), open_answer=None)
                    answer.save()
        return HttpResponseRedirect(reverse("forms:view-response-detail", kwargs={'pk': self.response.id}))
        '''
        else:
            return render(request, 'forms/responses/update-response.html', 
                          { 'form': ResponseForm(request.POST, formQs=self.form_questions, response=self.response), 
                           'form_meta':self.form_meta, 'response': self.response,
                           'msg':'Double check that all the fields are correctly filled out.' })
        '''
class DeleteResponse(LoginRequiredMixin, generic.DeleteView):
    model=Response
    def get_success_url(self):
        return reverse_lazy('forms:view-respondent-detail', kwargs={'pk': self.object.respondent.id})