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


class RecordResponse(LoginRequiredMixin, View):
    def get(self, request, pk, rid=None):
        form = Form.objects.filter(id=pk).first()
        formQuestions = FormQuestion.objects.filter(form=form).order_by('index')
        user_org = self.request.user.userprofile.organization
        response = None
        if rid:
            response = Response.objects.filter(id=rid).first()
        return render(request, 'forms/responses/record-response.html', 
                    { 'form': ResponseForm(formQuestions=formQuestions, response=response),
                     'user_org':user_org, 'response': response,
                    'form_meta': form
                    })
    
    def post(self, request, pk, rid=None):
        form = Form.objects.filter(id=pk).first()
        formQuestions = FormQuestion.objects.filter(form=form).order_by('index')
        if rid:
            response = Response.objects.filter(id=rid).first()
            if not response:
                print('WARNING: No response found, aborting upload!')
                return HttpResponseRedirect(reverse("forms:view-forms-index"))
            response.updated_at = timezone.now()
        else:
            respondentID = request.POST.get('Respondent')
            respondent = Respondent.objects.filter(id=respondentID).first()
            if not respondent:
                print('WARNING: No respondent found, aborting upload!')
                return HttpResponseRedirect(reverse("forms:view-forms-index"))
            checkResponse = Response.objects.filter(form=form, respondent=respondent).first()
            flag = False
            if checkResponse:
                flag = True
            response = Response(form=form, respondent=respondent, created_by=request.user, flag=flag)
        response.save()

        for fq in formQuestions:
            question = fq.question
            value = request.POST.get(str(fq.id))
            if question.question_type == 'Multiple Selections':
                answer = Answer.objects.filter(question = question, response = response)
                for a in answer:
                    answer.delete()
            else:
                answer = Answer.objects.filter(question = question, response = response).first()
            if not value:
                if answer:
                    for a in answer:
                        answer.delete()
                continue
            if not answer:
                answer = Answer(response=response, question=question)

            if question.question_type in ['Yes/No', 'Text', 'Number']:
                answer.open_answer = value
                answer.option = None
                answer.save()
            if question.question_type == 'Single Selection':
                option = Option.objects.filter(id=value).first()
                if option:
                    answer.option = option
                    answer.open_answer = None
                    answer.save()
                else:
                    answer.delete()
            if question.question_type == 'Multiple Selections':
                selectedOptions = request.POST.getlist(str(fq.id))
                for so in selectedOptions:
                    option = Option.objects.filter(id=so).first()
                    if not option or option.special == 'None of the above':
                        continue
                    elif option.special == 'All':
                        options = Option.objects.filter(question = question)
                        for option in options:
                            if not option.special:
                                answer = Answer(response=response, question=question,  option=option, open_answer=None)
                                answer.save()
                        continue
                    answer = Answer(response=response, question=question,  option=option, open_answer=None)
                    answer.save()
        return HttpResponseRedirect(reverse("forms:view-forms-index"))

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
        form_meta = get_object_or_404(Form, id=pk)
        form_structure = FormQuestion.objects.filter(form=form_meta).order_by('index')
        form_questions = [fq.question for fq in form_structure]
        fqIDs = [fq.id for fq in form_structure]
        form = ResponseForm(request.POST, formQs=form_questions, fqIDs = fqIDs)

        respondent_id = request.POST.get('Respondent')
        checkResponse = Response.objects.filter(form=form_meta, respondent=respondent_id).first()
        flag = False
        if checkResponse:
            flag = True
        respondent = Respondent.objects.filter(id=respondent_id).first()
        if not respondent:
            print('WARNING: No respondent found.')
            return
        response = Response(form=form_meta, respondent=respondent, created_by=request.user, flag=flag)
        
        response.save()
        for i in range(len(form_questions)):
            if request.POST.get(form_questions[i].question_text) == '':
                continue
            if form_questions[i].question_type == 'Text' or form_questions[i].question_type == 'Number':
                openResponse = request.POST.get(form_questions[i].question_text)
                answer = Answer(response=response, question=form_questions[i], open_answer=openResponse, option=None)
                answer.save()
            if form_questions[i].question_type == 'Yes/No':
                yesNo = request.POST.get(form_questions[i].question_text)
                answer = Answer(response=response, question=form_questions[i], open_answer=yesNo)
                answer.save()
            if form_questions[i].question_type == 'Single Selection':
                option_id = request.POST.get(form_questions[i].question_text)
                option = Option.objects.filter(id=option_id).first()
                if not option:
                    continue
                answer = Answer(response=response, question=form_questions[i], option=option, open_answer=None)
                answer.save()
            if form_questions[i].question_type == 'Multiple Selections':
                selected_options = request.POST.getlist(form_questions[i].question_text)
                #check if the options selected is none, and if so record nothing
                for o in range(len(selected_options)):
                    option = Option.objects.filter(id=selected_options[o]).first()
                    if not option:
                        continue
                    if option.special == 'None of the above':
                        continue
                    elif option.special == 'All':
                        options = Option.objects.filter(question = form_questions[i])
                        for option in options:
                            if not option.special:
                                answer = Answer(response=response, question=form_questions[i],  option=option, open_answer=None)
                                answer.save()
                        continue
                    answer = Answer(response=response, question=form_questions[i],  option=get_object_or_404(Option, pk=selected_options[o]), open_answer=None)
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
    def get(self, request, pk, rid):
        response = get_object_or_404(Response, id=rid)
        form_meta = Form.objects.filter(id=response.form.id).first()
        form_structure = FormQuestion.objects.filter(form=form_meta).order_by('index')
        fqIDs = [fq.id for fq in form_structure]
        form_questions = [fq.question for fq in form_structure]
        user_org = request.user.userprofile.organization
        return render(request, 'forms/responses/update-response.html', 
                    { 'form': ResponseForm(formQs=form_questions, fqIDs=fqIDs, response=response),
                     'user':request.user, 'user_org':user_org,
                    'form_meta': form_meta,
                    'response': response})

    def post(self, request, pk):
        response = Response.objects.filter(id=pk).first()
        if not response:
            print('WARNING: Response not found...')
            return
        form_meta = Form.objects.filter(id=response.form.id).first()
        form_structure = FormQuestion.objects.filter(form=form_meta).order_by('index')
        fqIDs = [fq.id for fq in form_structure]
        form_questions = [fq.question for fq in form_structure]
        form = ResponseForm(request.POST, formQs=form_questions, fqIDs=fqIDs, response=response)

        #if form.is_valid():
        response.updated_at = timezone.now()
        response.save()

        for i in range(len(form_questions)):
            if form_questions[i].question_type == 'Text' or form_questions[i].question_type == 'Number':
                openResponse = request.POST.get(form_questions[i].question_text)
                answer = Answer.objects.filter(response = response, question=form_questions[i]).first()
                if not answer:
                    continue
                answer.open_answer = openResponse
                answer.save()
            if form_questions[i].question_type == 'Yes/No':
                yesNo = request.POST.get(form_questions[i].question_text)
                answer = Answer.objects.filter(response = response, question=form_questions[i]).first()
                if not answer:
                    continue
                answer.open_answer = yesNo
                answer.save()
            if form_questions[i].question_type == 'Single Selection':
                option_id = request.POST.get(form_questions[i].question_text)
                option = Option.objects.filter(id=option_id).first()
                if not option:
                    continue
                answer = Answer.objects.filter(response = response, question=form_questions[i]).first()
                answer.option = option
                answer.save()
            if form_questions[i].question_type == 'Multiple Selections':
                selected_options = request.POST.getlist(form_questions[i].question_text)
                previous_answers =  Answer.objects.filter(response = response, question=form_questions[i])
                for answer in previous_answers:
                    answer.delete()
                for o in range(len(selected_options)):
                    option_id = request.POST.get(form_questions[i].question_text)
                    option = Option.objects.filter(id=option_id).first()
                    if not option:
                        continue
                    if option.special == 'None of the above':
                        continue
                    elif option.special == 'All':
                        options = Option.objects.filter(question = form_questions[i])
                        for option in options:
                            if not option.special:
                                answer = Answer(response=response, question=form_questions[i],  option=option, open_answer=None)
                                answer.save()
                        continue
                    answer = Answer(response=response, question=form_questions[i],  option=option, open_answer=None)
                    answer.save()
        return HttpResponseRedirect(reverse("forms:view-response-detail", kwargs={'pk': response.id}))
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