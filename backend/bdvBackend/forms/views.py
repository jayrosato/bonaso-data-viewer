from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
import datetime
from django.views import generic, View
from django.http import JsonResponse
from django.views.decorators.csrf import requires_csrf_token
import json

from .forms import ResponseForm, QuestionForm, FormsForm, FormQuestionForm, QuestionSelector
from datetime import datetime

import csv
from django.db.models import Q, Count

from.models import Respondent, Form, FormQuestion, Question, Option, Response, Answer, Organization, User, UserProfile, FormLogic, FormLogicRule
now = timezone.now()

#views related to forms
class ViewFormsIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/forms/view-forms-index.html'
    context_object_name = 'active_forms'
    
    def get_queryset(self):
        return Form.objects.filter(start_date__lte= datetime.today(), end_date__gte = datetime.today()).order_by('organization')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        return context
    
class ViewFormDetail(LoginRequiredMixin, generic.DetailView):
    model=Form
    template_name = 'forms/forms/view-form-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        form = self.get_object()
        responses = Response.objects.filter(form=form)
        form_structure = FormQuestion.objects.filter(form=form).order_by('index')
        form_questions = []
        for i in range(len(form_structure)):
            fq = form_structure[i]
            question = fq.question 
            options = Option.objects.filter(question=question.id)
            logic = FormLogic.objects.filter(conditional_question = form_structure[i]).first()
            if logic:
                rules = FormLogicRule.objects.filter(form_logic=logic)
            else:
                rules = None
            form_questions.append({
                'form_question': fq,
                'question': question,
                'options': options,
                'logic': logic,
                'rules': rules
            })
        context['form'] = form
        context['form_structure'] = form_structure
        context['form_questions'] = form_questions
        return context

#new form stuff
class CreateForm(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'forms/forms/create-form-all.html', 
                          { 'form': FormsForm(organization=request.user.userprofile.organization), 
                           'form_question':FormQuestionForm(),
                           'msg':'Double check that all the fields are correctly filled out.' })

    def post(self, request):
        form = Form(
            form_name = request.POST.get('form_name'),
            organization = get_object_or_404(Organization, id=request.POST.get('organization')),
            start_date = request.POST.get('start_date'),
            end_date = request.POST.get('end_date'),
            created_by = self.request.user
            )
        form.save()
        questions = request.POST.getlist('question')
        print(questions)
        print(request.POST.getlist('parent_question'))
        for i in range(len(questions)):
            #create FormQuestion
            formQ = FormQuestion(
            form=form,
            index = i,
            question = get_object_or_404(Question, id=questions[i]),
            )
            formQ.save()
            #check for and create conditions
            if request.POST.get(f'logic[question-{i+1}][on_match]'):
                if request.POST.get(f'logic[question-{i+1}][on_match]'):
                    if request.POST.get(f'logic[question-{i+1}][limit_options]') == 'on':
                        limitOptions = True
                    else:
                        limitOptions = False
                formLogic = FormLogic(
                    form=form,
                    conditional_question = formQ,
                    on_match = request.POST.get(f'logic[question-{i+1}][on_match]'),
                    conditional_operator = request.POST.get(f'logic[question-{i+1}][operator]'),
                    limit_options = limitOptions
                )
                formLogic.save()
                for k in range(len(request.POST.getlist(f'logic[question-{i+1}][parent_question]'))):
                    pqId = request.POST.getlist(f'logic[question-{i+1}][parent_question]')[k]
                    parentFormQuestion = get_object_or_404(FormQuestion, question=pqId, form=form.id)
                    try:
                        if request.POST.getlist(f'logic[question-{i+1}][value_comparison]')[k]:
                            valueComp = valueComp = request.POST.getlist(f'logic[question-{i+1}][value_comparison]')[k]
                        else:
                            valueComp = None
                    except(IndexError):
                        valueComp = None
                    try:    
                        if request.POST.getlist(f'logic[question-{i+1}][negate_value]')[k]:
                            negateValue = True
                        else:
                            negateValue = False
                    except(IndexError):
                        negateValue = False
                    formLogicRule = FormLogicRule(
                        form_logic = formLogic,
                        parent_question = parentFormQuestion,
                        expected_values = request.POST.getlist(f'logic[question-{i+1}][expected_values]')[k],
                        value_comparison = valueComp,
                        negate_value = negateValue,
                    )
                    formLogicRule.save()
        return HttpResponseRedirect(reverse('forms:view-form-detail', kwargs={'pk': form.id}))


class UpdateForm(LoginRequiredMixin, View):
    def get(self, request, pk):
        form = get_object_or_404(Form, id=pk)
        formQs = FormQuestion.objects.filter(form = form.id).order_by('index')
        formQForms = [FormQuestionForm(instance=fq) for fq in formQs]
        return render(request, 'forms/forms/update-form-all.html', 
                          { 'form_meta':form, 'user_org':request.user.userprofile.organization,
                            'form': FormsForm(organization=request.user.userprofile.organization,instance=form), 
                           'form_question':formQForms,
                           'msg':'Double check that all the fields are correctly filled out.' })

    def post(self, request, pk):
        form = get_object_or_404(Form, id=pk)
        form.form_name = request.POST.get('form_name')
        form.organization = get_object_or_404(Organization, id=request.POST.get('organization'))
        form.start_date = request.POST.get('start_date')
        form.end_date = request.POST.get('end_date')
        form.save()

        questions = request.POST.getlist('question')

        existingQuestions = FormQuestion.objects.filter(form=form.id)
        if len(existingQuestions) > len(questions):
            for extra in existingQuestions[len(questions):]:
                extra.delete()

        for i in range(len(questions)):
            if i+1 <= len(existingQuestions):
                formQ = existingQuestions[i]
                formQ.index = i
                formQ.question = get_object_or_404(Question, id=questions[i])
                formQ.save()
                if request.POST.get(f'logic[question-{i+1}][on_match]'):
                    if request.POST.get(f'logic[question-{i+1}][limit_options]') == 'on':
                        limitOptions = True
                    else:
                        limitOptions = False

                    formLogic = FormLogic.objects.filter(conditional_question=formQ.id).first()
                    if formLogic:
                        formLogic.conditional_question = formQ
                        formLogic.on_match = request.POST.get(f'logic[question-{i+1}][on_match]')
                        formLogic.conditional_operator = request.POST.get(f'logic[question-{i+1}][operator]')
                        formLogic.limit_options = limitOptions
                    else:
                        formLogic = FormLogic(
                            form=form,
                            conditional_question = formQ,
                            on_match = request.POST.get(f'logic[question-{i+1}][on_match]'),
                            conditional_operator = request.POST.get(f'logic[question-{i+1}][operator]'),
                            limit_options = limitOptions
                            )
                    formLogic.save()
                    existingRules = FormLogicRule.objects.filter(form_logic=formLogic.id)
                    rules = request.POST.getlist(f'logic[question-{i+1}][parent_question]')
                    if len(rules) < len(existingRules):
                        for extra in existingRules[len(rules):]:
                            extra.delete()

                    for k in range(len(rules)):
                        print(request.POST.getlist(f'logic[question-{i+1}][expected_values]'), request.POST.getlist(f'logic[question-{i+1}][value_comparison]'))
                        if k+1 <= len(existingRules):
                            rule = existingRules[k]
                            pqId = request.POST.getlist(f'logic[question-{i+1}][parent_question]')[k]
                            parentFormQuestion = get_object_or_404(FormQuestion, question=pqId, form=form.id)
                            try:
                                if request.POST.getlist(f'logic[question-{i+1}][value_comparison]')[k]:
                                    valueComp = valueComp = request.POST.getlist(f'logic[question-{i+1}][value_comparison]')[k]
                                else:
                                    valueComp = None
                            except(IndexError):
                                valueComp = None
                            try:    
                                if request.POST.getlist(f'logic[question-{i+1}][negate_value]')[k]:
                                    negateValue = True
                                else:
                                    negateValue = False
                            except(IndexError):
                                negateValue = False
                            rule.parent_question = parentFormQuestion 
                            rule.expected_values = request.POST.getlist(f'logic[question-{i+1}][expected_values]')[k]
                            rule.value_comparison = valueComp
                            rule.negate_value = negateValue
                            rule.save()
                        else:
                            pqId = request.POST.getlist(f'logic[question-{i+1}][parent_question]')[k]
                            parentFormQuestion = get_object_or_404(FormQuestion, question=pqId, form=form.id)
                            try:
                                if request.POST.getlist(f'logic[question-{i+1}][value_comparison]')[k]:
                                    valueComp = valueComp = request.POST.getlist(f'logic[question-{i+1}][value_comparison]')[k]
                                else:
                                    valueComp = None
                            except(IndexError):
                                valueComp = None
                            try:    
                                if request.POST.getlist(f'logic[question-{i+1}][negate_value]')[k]:
                                    negateValue = True
                                else:
                                    negateValue = False
                            except(IndexError):
                                negateValue = False
                            formLogicRule = FormLogicRule(
                                form_logic = formLogic,
                                parent_question = parentFormQuestion,
                                expected_values = request.POST.getlist(f'logic[question-{i+1}][expected_values]')[k],
                                value_comparison = valueComp,
                                negate_value = negateValue,
                            )
                            formLogicRule.save()
                else: 
                    formLogic = FormLogic.objects.filter(conditional_question=formQ.id).first()
                    if formLogic:
                        existingRules = FormLogicRule.objects.filter(form_logic=formLogic.id)
                        for rule in existingRules:
                            rule.delete()
                        formLogic.delete()
            else:
                formQ = FormQuestion(
                    form=form,
                    index = i,
                    question = get_object_or_404(Question, id=questions[i]),
                )
                if request.POST.get(f'logic[question-{i+1}][on_match]'):
                    if request.POST.get(f'logic[question-{i+1}][limit_options]') == 'on':
                        limitOptions = True
                    else:
                        limitOptions = False

                formQ.save()
                if request.POST.get(f'logic[question-{i+1}][on_match]'):
                    formLogic = FormLogic(
                    form=form,
                    conditional_question = formQ,
                    on_match = request.POST.get(f'logic[question-{i+1}][on_match]'),
                    conditional_operator = request.POST.get(f'logic[question-{i+1}][operator]'),
                    limit_options = limitOptions
                    )
                    formLogic.save()
                for k in range(len(request.POST.getlist(f'logic[question-{i+1}][parent_question]'))):
                    pqId = request.POST.getlist(f'logic[question-{i+1}][parent_question]')[k]
                    parentFormQuestion = get_object_or_404(FormQuestion, question=pqId, form=form.id)
                    try:
                        if request.POST.getlist(f'logic[question-{i+1}][value_comparison]')[k]:
                            valueComp = valueComp = request.POST.getlist(f'logic[question-{i+1}][value_comparison]')[k]
                        else:
                            valueComp = None
                    except(IndexError):
                        valueComp = None

                    try:    
                        if request.POST.getlist(f'logic[question-{i+1}][negate_value]')[k]:
                            negateValue = True
                        else:
                            negateValue = False
                    except(IndexError):
                        negateValue = False
                    formLogicRule = FormLogicRule(
                        form_logic = formLogic,
                        parent_question = parentFormQuestion,
                        expected_values = request.POST.getlist(f'logic[question-{i+1}][expected_values]')[k],
                        value_comparison = valueComp,
                        negate_value = negateValue,
                    )
                    formLogicRule.save()
        return HttpResponseRedirect(reverse('forms:view-form-detail', kwargs={'pk': form.id}))
    
class DeleteForm(LoginRequiredMixin, generic.DeleteView):
    model=Form
    success_url = reverse_lazy('forms:view-forms-index')


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
                    option = Option(question = question, option_text=options[i])
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

    #options are currently assuming same load order
    #should probably add some validation logic here (at least for length/remove blanks)
    def post(self, request, pk):
        try:
            data = json.loads(request.body)
            question = get_object_or_404(Question, id=pk)
            question.question_text = data.get('question_text')
            question.question_type = data.get('question_type')
            question.save()
            options = data.get('options')
            existingOptions = Option.objects.filter(question=question.id)
            if len(existingOptions) > len(options):
                for extra in existingOptions[len(options):]:
                    extra.delete()

            if len(options) > 0:
                for i in range(len(options)):
                    if i+1 <= len(existingOptions):
                        option = existingOptions[i]
                        option.option_text = options[i]
                        option.save()
                    else:
                        option = Option(question = question, option_text=options[i])
                        option.save()
            return JsonResponse({'redirect': reverse('forms:view-questions')})
        except:
            print('Ah nuts')


class DeleteQuestion(LoginRequiredMixin, generic.DeleteView):
    model=Question
    def get_success_url(self):
        return reverse_lazy('forms:view-questions')


#views related to responses
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
        user_org = self.request.user.userprofile.organization
        return render(request, 'forms/responses/create-response.html', 
                    { 'form': ResponseForm(formQs=self.form_questions),
                     'user_org':user_org,
                    'form_meta': self.form_meta,})

    def post(self, request, pk):
        self.form_meta = get_object_or_404(Form, id=pk)
        self.form_structure = FormQuestion.objects.filter(form=self.form_meta).order_by('index')
        self.form_questions = [fq.question for fq in self.form_structure]
        self.form = ResponseForm(request.POST, formQs=self.form_questions, formLogic=self.form_structure)

        if self.form.is_valid():
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
                    for o in range(len(selected_options)):
                        answer = Answer(response=response, question=self.form_questions[i],  option=get_object_or_404(Option, pk=selected_options[o]), open_answer=None)
                        answer.save()
            return HttpResponseRedirect(reverse("forms:view-forms-index"))
        else:
            return render(request, 'forms/responses/create-response.html', 
                          { 'form': ResponseForm(request.POST, formQs=self.form_questions, formLogic=self.form_structure), 
                           'form_meta':self.form_meta, 
                           'msg':'Double check that all the fields are correctly filled out.' })

class UpdateResponse(LoginRequiredMixin, View):
    def get(self, request, pk):
        self.response = get_object_or_404(Response, id=pk)
        self.form_meta = Form.objects.filter(id=self.response.form.id).first()
        self.form_structure = FormQuestion.objects.filter(form=self.form_meta).order_by('index')
        self.form_questions = [fq.question for fq in self.form_structure]
        user_org = self.request.user.userprofile.organization
        return render(request, 'forms/responses/update-response.html', 
                    { 'form': ResponseForm(formQs=self.form_questions, formLogic=self.form_structure, response=self.response),
                     'user':self.request.user, 'user_org':user_org,
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
            return HttpResponseRedirect(reverse("forms:view-response-detail", kwargs={'pk': self.response.id}))
        else:
            return render(request, 'forms/responses/update-response.html', 
                          { 'form': ResponseForm(request.POST, formQs=self.form_questions, formLogic=self.form_structure, response=self.response), 
                           'form_meta':self.form_meta, 'response': self.response,
                           'msg':'Double check that all the fields are correctly filled out.' })

class DeleteResponse(LoginRequiredMixin, generic.DeleteView):
    model=Response
    def get_success_url(self):
        return reverse_lazy('forms:view-respondent-detail', kwargs={'pk': self.object.respondent.id})


class ViewRespondentsIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/respondents/view-respondents-index.html'
    context_object_name = 'respondents'
    def get_queryset(self):
        return Respondent.objects.all()

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
    fields = [
            'id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship', 'ward', 'village', 
            'district', 'email', 'contact_no', 'created_by'
            ]
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        form.fields['created_by'].queryset = User.objects.filter(id=user.id)
        form.fields['created_by'].initial = User.objects.filter(id=user.id)
        return form
    
    def get_success_url(self):
        return reverse_lazy('forms:view-respondent-detail', kwargs={'pk': self.object.id})


class UpdateRespondent(LoginRequiredMixin, generic.UpdateView):
    model=Respondent
    template_name = 'forms/respondents/update-respondent.html'
    fields = [
            'id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship', 'ward', 'village', 
            'district', 'email', 'contact_no'
            ]
    def get_success_url(self):
        return reverse_lazy('forms:view-respondent-detail', kwargs={'pk': self.object.id})
   

class DeleteRespondent(LoginRequiredMixin, generic.DeleteView):
    model=Respondent
    success_url = reverse_lazy('forms:view-respondents-index')



class ViewOrgsIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/orgs/view-orgs-index.html'
    context_object_name = 'organizations'
    def get_queryset(self):
        return Organization.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        return context

class ViewOrgDetail(LoginRequiredMixin, generic.DetailView):
    model=Organization
    template_name='forms/orgs/view-org-detail.html'
    context_object_name = 'organization'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        pk = self.kwargs['pk']
        child_orgs = Organization.objects.filter(parent_organization = pk)
        context['user_org'] = user_org
        context['child_orgs'] = child_orgs
        return context

class CreateOrg(LoginRequiredMixin, generic.CreateView):
    model=Organization
    template_name = 'forms/orgs/update-org.html'
    fields = [
            'organization_name', 'parent_organization'
            ]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_org = self.request.user.userprofile.organization
        if user_org.id != 3:
            if user_org.parent_organization:
                form.fields['parent_organization'].queryset = Organization.objects.filter(id=user_org.parent_organization.id)
            else:
                form.fields['parent_organization'].queryset = Organization.objects.filter(Q(id=user_org.id) | Q(id=user_org.parent_organization))
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        context['update'] = False
        return context
    
    def get_success_url(self):
        return reverse_lazy('forms:view-org-detail', kwargs={'pk': self.object.id})

class UpdateOrg(LoginRequiredMixin, generic.UpdateView):
    model=Organization
    template_name = 'forms/orgs/update-org.html'
    fields = [
            'organization_name', 'parent_organization'
            ]
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_org = self.request.user.userprofile.organization
        if user_org.id != 3:
            if user_org.parent_organization:
                form.fields['parent_organization'].queryset = Organization.objects.filter(id=user_org.parent_organization.id)
            else:
                form.fields['parent_organization'].queryset = Organization.objects.filter(Q(id=user_org.id) | Q(id=user_org.parent_organization))
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        context['update'] = True
        return context
    
    def get_success_url(self):
        return reverse_lazy('forms:view-org-detail', kwargs={'pk': self.object.id})
    
class DeleteOrg(LoginRequiredMixin, generic.DeleteView):
    model=Organization
    success_url = reverse_lazy('forms:view-orgs-index')

class EmployeesIndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/orgs/view-employees-index.html'
    context_object_name = 'employees'
    def get_queryset(self):
        return User.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        return context

class EmployeeDetailView(LoginRequiredMixin, generic.DetailView):
    model=User
    template_name='forms/orgs/view-employee-detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        pk=self.kwargs['pk']
        employee = get_object_or_404(User, id=pk)
        responses = Response.objects.filter(created_by=employee.id).count()
        context['responses'] = responses
        respondents = Respondent.objects.filter(created_by=employee.id).count()
        context['respondents'] = respondents
        forms = Form.objects.filter(created_by=employee.id).count()
        context['forms'] = forms
        direct_team = UserProfile.objects.filter(supervisor=employee.id).count()
        underlings = UserProfile.objects.filter(manager=employee.id).count()
        context['direct_team'] = direct_team
        context['underlings'] = underlings

        try:
            employee_user_profile = employee.userprofile
        except UserProfile.DoesNotExist:
            employee_user_profile = None

        context['employee_user_profile'] = employee_user_profile
        return context

class CreateUser(LoginRequiredMixin, generic.CreateView):
    model = UserProfile
    fields = '__all__'
    template_name = 'forms/orgs/create-user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        return context
    
    def get_success_url(self):
        return reverse_lazy('forms:view-employee-detail', kwargs={'pk': self.object.id})

class Settings(LoginRequiredMixin, View):
    def get(self, request):
        user = self.request.user
        userProfile = user.userprofile
        return render(request, 'forms/settings.html', {'user':user, 'userProfile':userProfile})

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'forms/dashboard-creator.html')

class GetQuestions(LoginRequiredMixin, View):
    def get(self, request):
        questions = Question.objects.all()
        data = {
            'labels':[q.question_text for q in questions],
            'ids':[q.id for q in questions]
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

#this is an 'api' used during form creation to make conditional question logic easier for the user
class GetQuestionInfo(LoginRequiredMixin, View):
    def get(self, request, pk):
        question = Question.objects.filter(id=pk).first()
        options = Option.objects.filter(question=question.id)
        if options:
            option_ids = [option.id for option in options]
            option_text = [option.option_text for option in options]
        else:
            option_ids = []
            option_text = []
        data = {
            'question_type': question.question_type,
            'option_ids': option_ids,
            'option_text':option_text
        }
        return JsonResponse(data) 

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
            print('open', options_count)
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
class GetFormQuestionByIndex(LoginRequiredMixin, View):
    def get(self, request, form, index):
        formQuestion = FormQuestion.objects.filter(form=form, index=index).first()
        formLogic = FormLogic.objects.filter(conditional_question=formQuestion.id).first()
        if formLogic:
            formLogicRules = FormLogicRule.objects.filter(form_logic=formLogic.id)
            data = {
                'on_match':formLogic.on_match,
                'conditional_operator':formLogic.conditional_operator,
                'limit_options': formLogic.limit_options,
                'rules':[{
                    'parent_question':[rule.parent_question.question.id for rule in formLogicRules],
                    'parent_question_index':[rule.parent_question.index for rule in formLogicRules],
                    'expected_values':[rule.expected_values for rule in formLogicRules],
                    'value_comparison':[rule.value_comparison for rule in formLogicRules],
                    'negate_value':[rule.negate_value for rule in formLogicRules]
                }]
            }
        else:
            data = {}
        return JsonResponse(data)


class Data(LoginRequiredMixin, View):        
    def get(self, request):
        return render(request, 'forms/data.html', 
        {'form':QuestionSelector()})
    
class FormTemplate(LoginRequiredMixin, View):
    def get(self, request, pk):
        form = Form.objects.filter(id=pk).first()
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="form_template_{form.id}_{form}.csv"'},
        )
        form_structure = FormQuestion.objects.filter(form=form.id).order_by('index')
        form_questions = [fq.question for fq in form_structure]

        respondent_fields = [field.name for field in Respondent._meta.get_fields()]
        respondent_fields.remove('response')
        respondent_fields.remove('id')
        respondent_fields.remove('created_at')
        respondent_fields.remove('updated_at')
        question_fields = [q.question_text for q in form_questions]

        fields = respondent_fields + question_fields
        writer = csv.writer(response)
        writer.writerow(fields)

        return response
    
    def post(self, request, pk):
        form_meta = get_object_or_404(Form, id=pk)
        form_structure = FormQuestion.objects.filter(form=form_meta).order_by('index')
        form_questions = [fq.question for fq in form_structure]
        if form_questions:
            csv_file = request.FILES['template']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                checkRespondent = Respondent.objects.filter(id_no=row['id_no']).first()
                raw_date = row['dob'].strip().replace('“', '').replace('”', '').replace('"', '')
                try:
                    parsed_date = datetime.strptime(raw_date, '%m/%d/%Y').date()
                except ValueError:
                    raise ValueError(f"Invalid date format: {raw_date}. Expected MM/DD/YYYY.")
                if not checkRespondent:
                    respondent = Respondent(id_no=row['id_no'], fname=row['fname'], lname=row['lname'], dob=parsed_date, sex=row['sex'], ward=row['ward'], village=row['village'], district=row['district'], citizenship=row['citizenship'], email=row['email'], contact_no=row['contact_no'])
                    respondent.save()
                #currently this defaults to updating automatially, but we probably shouldn't do that
                else:
                    respondent = checkRespondent
                    respondent.fname = row['fname']
                    respondent.lname = row['lname']
                    respondent.dob = parsed_date
                    respondent.sex = row['sex']
                    respondent.ward = row['ward']
                    respondent.village = row['village']
                    respondent.district = row['district']
                    respondent.citizenship = row['citizenship']
                    respondent.email = row['email']
                    respondent.contact_no = row['contact_no']
                    respondent.save()
                checkResponse = Response.objects.filter(form = form_meta.id, respondent = respondent.id).first()
                print(checkResponse)
                if checkResponse:
                    print(f'Response from {respondent} has already been recorded for this form. To edit this response, please do so using the edit responses option.')
                    continue
                response = Response(respondent=respondent, form=form_meta, created_by=request.user)
                response.save()
                for i in range(len(form_questions)):
                    if form_questions[i].question_type == 'Text' or form_questions[i].question_type == 'Number':
                        openResponse = row[form_questions[i].question_text]
                        answer = Answer(response=response, question=form_questions[i], open_answer=openResponse, option=None)
                        answer.save()
                    if form_questions[i].question_type == 'Yes/No':
                        yesNo = row[form_questions[i].question_text]
                        answer = Answer(response=response, question=form_questions[i], open_answer=yesNo)
                        answer.save()
                    if form_questions[i].question_type == 'Single Selection':
                        option_id = row[form_questions[i].question_text]
                        try:
                            answer = Answer(response=response, question=form_questions[i],  option=get_object_or_404(Option, pk=option_id), open_answer=None)
                            answer.save()
                        except(ValueError):
                            text = option_id.strip()
                            answer = Answer(response=response, question=form_questions[i], option=Option.objects.filter(option_text=text, question=form_questions[i].id).first(), open_answer=None)
                            answer.save()
                    if form_questions[i].question_type == 'Multiple Selections':
                        selected_options = row[form_questions[i].question_text].split(',')
                        for o in range(len(selected_options)):
                            try:
                                answer = Answer(response=response, question=form_questions[i],  option=get_object_or_404(Option, pk=selected_options[o]), open_answer=None)
                                answer.save()
                            except(ValueError):
                                text = selected_options[o].strip()
                                answer = Answer(response=response, question=form_questions[i], option=Option.objects.filter(option_text=text, question=form_questions[i].id).first(), open_answer=None)
                                answer.save()
        return HttpResponseRedirect(reverse("forms:view-form-detail", kwargs={'pk': form_meta.id}))
                