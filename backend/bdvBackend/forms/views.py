from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
import datetime
from django.views import generic, View

from .forms import RespondentForm, SelectRespondentForm, ResponseForm

import datetime
from django.db.models import F, Count


from.models import Respondent, Form, FormQuestion, Question, Option, Response, Answer
now = timezone.now()

#views related to forms
class ViewFormsIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/view-forms-index.html'
    context_object_name = 'active_forms'
    
    def get_queryset(self):
        num_visits = self.request.session.get('num_visits',0)
        num_visits += 1
        self.request.session['num_visits'] = num_visits
        last_login = self.request.session.get('last_login', 0)
        last_login = now.isoformat()
        self.request.session['last_login'] = last_login

        return Form.objects.filter(start_date__lte= datetime.date.today(), end_date__gte = datetime.date.today()).order_by('organization')

class ViewFormDetail(LoginRequiredMixin, generic.DetailView):
    model=Form
    template_name = 'forms/view-form-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.form = self.get_object()
        self.responses = Response.objects.filter(form=self.form)
        self.form_structure = FormQuestion.objects.filter(form=self.form).order_by('index')
        self.form_questions = [fq.question for fq in self.form_structure]
        self.options_list = []
        for i in range(len(self.form_questions)):  
            options = Option.objects.filter(question=self.form_questions[i])
            if options:
                self.options_list.append(options)
            else: 
                self.options_list.append([])
        context['form'] = self.form
        context['form_structure'] = self.form_structure
        context['question_option_pairs'] = zip(self.form_structure, self.form_questions, self.options_list)
        return context

class CreateForm(LoginRequiredMixin, generic.CreateView):
    model = Form
    template_name = 'forms/update-form.html'
    fields = [
            'form_name', 'start_date', 'end_date', 'organization'
            ]
    def get_success_url(self):
        return reverse_lazy('forms:view-form-detail', kwargs={'pk': self.object.id})


class UpdateForm(LoginRequiredMixin, generic.UpdateView):
    model=Form
    template_name = 'forms/update-form.html'
    fields = [
            'form_name', 'start_date', 'end_date', 'organization'
            ]
    def get_success_url(self):
        return reverse_lazy('forms:view-form-detail', kwargs={'pk': self.object.id})
   
class DeleteForm(LoginRequiredMixin, generic.DeleteView):
    model=Form
    success_url = reverse_lazy('forms:view-forms-index')

#view related to form questions
class CreateFormQuestion(LoginRequiredMixin, generic.CreateView):
    model = FormQuestion
    template_name = 'forms/update-form-question.html'
    fields = [
            'question', 'visible_if_question', 'visible_if_answer', 'index'
            ]
    
    def form_valid(self, form):
        form_id = self.kwargs.get('form_id')
        form.instance.form_id = form_id
        return super().form_valid(form)
    
    def get_success_url(self):
        print(self.object.form.id)
        return reverse_lazy('forms:view-form-detail', kwargs={'pk': self.object.form.id})


class UpdateFormQuestion(LoginRequiredMixin, generic.UpdateView):
    model = FormQuestion
    template_name = 'forms/update-form-question.html'
    fields = [
            'question', 'visible_if_question', 'visible_if_answer', 'index'
            ]
    
    def form_valid(self, form):
        form_id = self.kwargs.get('form_id')
        form.instance.form_id = form_id
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('forms:view-form-detail', kwargs={'pk': self.object.form.id})

class RemoveFormQuestion(LoginRequiredMixin, generic.DeleteView):
    model=FormQuestion
    def get_success_url(self):
        return reverse_lazy('forms:view-form-detail', kwargs={'pk': self.object.form.id})




#views related to responses
class ViewResponseDetail(LoginRequiredMixin, generic.DetailView):
    model=Response
    template_name = 'forms/view-response-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response = self.get_object()
        form = Form.objects.filter(id = response.form.id).first()
        formQs = FormQuestion.objects.filter(form = form.id).order_by('index')
        form_questions = [fq.question for fq in formQs]
        answers = []
        for i in range(len(form_questions)):  
            answer = Answer.objects.filter(response=response, question=form_questions[i]).first()
            if answer:
                answers.append(answer)
            else: 
                answers.append('No response given.')
        print(form_questions)
        print(answers)
        context['response'] = response
        context['question_answer_pairs'] = zip(form_questions, answers)
        context['form_meta'] = form
        return context
    
class NewResponse(LoginRequiredMixin, View):
    def get(self, request, pk):
        self.form_meta = get_object_or_404(Form, id=pk)
        self.form_structure = FormQuestion.objects.filter(form=self.form_meta).order_by('index')
        self.form_questions = [fq.question for fq in self.form_structure]
        return render(request, 'forms/new-response.html', 
                    { 'form': ResponseForm(formQs=self.form_questions, formLogic=self.form_structure),
                    'form_meta': self.form_meta,})

    def post(self, request, pk):
        self.form_meta = get_object_or_404(Form, id=pk)
        self.form_structure = FormQuestion.objects.filter(form=self.form_meta).order_by('index')
        self.form_questions = [fq.question for fq in self.form_structure]
        self.form = ResponseForm(request.POST, formQs=self.form_questions, formLogic=self.form_structure)

        if self.form.is_valid():
            respondent_id = request.POST.get('Respondent')
            response = Response(form=self.form_meta, respondent=get_object_or_404(Respondent, pk=respondent_id))
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
                    for o in range(len(selected_options)):
                        answer = Answer(response=response, question=self.form_questions[i],  option=get_object_or_404(Option, pk=selected_options[o]), open_answer=None)
                        answer.save()
            return HttpResponseRedirect(reverse("forms:index"))
        else:
            return render(request, 'forms/form-detail.html', 
                          { 'form': ResponseForm(request.POST, formQs=self.form_questions, formLogic=self.form_structure), 
                           'form_meta':self.form_meta, 
                           'msg':'Double check that all the fields are correctly filled out.' })

class UpdateResponse(LoginRequiredMixin, View):
    def get(self, request, pk):
        self.response = get_object_or_404(Response, id=pk)
        self.form_meta = Form.objects.filter(id=self.response.form.id).first()
        self.form_structure = FormQuestion.objects.filter(form=self.form_meta).order_by('index')
        self.form_questions = [fq.question for fq in self.form_structure]
        return render(request, 'forms/update-response.html', 
                    { 'form': ResponseForm(formQs=self.form_questions, formLogic=self.form_structure, response=self.response),
                    'form_meta': self.form_meta,
                    'response': self.response})


    def post(self, request, pk):
        self.response = get_object_or_404(Response, id=pk)
        self.form_meta = Form.objects.filter(id=self.response.form.id).first()
        self.form_structure = FormQuestion.objects.filter(form=self.form_meta).order_by('index')
        self.form_questions = [fq.question for fq in self.form_structure]
        self.form = ResponseForm(request.POST, formQs=self.form_questions, formLogic=self.form_structure, response=self.response)


        if self.form.is_valid():
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
                        answer = Answer(response=self.response, question=self.form_questions[i],  option=get_object_or_404(Option, pk=selected_options[o]), open_answer=None)
                        answer.save()
            return HttpResponseRedirect(reverse("forms:index"))
        else:
            return render(request, 'forms/update-response.html', 
                          { 'form': ResponseForm(request.POST, formQs=self.form_questions, formLogic=self.form_structure, response=self.response), 
                           'form_meta':self.form_meta, 'response': self.response,
                           'msg':'Double check that all the fields are correctly filled out.' })

class DeleteResponse(LoginRequiredMixin, generic.DeleteView):
    model=Response
    def get_success_url(self):
        return reverse_lazy('forms:view-respondent-detail', kwargs={'pk': self.object.respondent.id})


class ViewRespondentsIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/view-respondents-index.html'
    context_object_name = 'respondents'
    def get_queryset(self):
        return Respondent.objects.all()

class ViewRespondentDetail(LoginRequiredMixin, generic.DetailView):
    model=Respondent
    template_name = 'forms/view-respondent-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        respondent = self.get_object()
        responses = Response.objects.filter(respondent=respondent).order_by('response_date')
        context['respondent'] = respondent
        context['responses'] = responses
        return context


class CreateRespondent(LoginRequiredMixin, generic.CreateView):
    model = Respondent
    template_name = 'forms/update-respondent.html'
    fields = [
            'id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship', 'ward', 'village', 
            'district', 'email', 'contact_no'
            ]
    def get_success_url(self):
        return reverse_lazy('forms:view-respondent-detail', kwargs={'pk': self.object.id})


class UpdateRespondent(LoginRequiredMixin, generic.UpdateView):
    model=Respondent
    template_name = 'forms/update-respondent.html'
    fields = [
            'id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship', 'ward', 'village', 
            'district', 'email', 'contact_no'
            ]
    def get_success_url(self):
        return reverse_lazy('forms:view-respondent-detail', kwargs={'pk': self.object.id})
   

class DeleteRespondent(LoginRequiredMixin, generic.DeleteView):
    model=Respondent
    success_url = reverse_lazy('forms:respondents')

    #logic for instance where respondent has responses would go here
