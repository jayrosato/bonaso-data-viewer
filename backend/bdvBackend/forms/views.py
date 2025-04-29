from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
import datetime
from django.views import generic, View
from django.http import JsonResponse
from django.views.decorators.csrf import requires_csrf_token
import json
    
from .forms import ResponseForm, QuestionForm, FormsForm, FormQuestionForm

import datetime
from django.db.models import Q


from.models import Respondent, Form, FormQuestion, Question, Option, Response, Answer, Organization
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        return context
    
class ViewFormDetail(LoginRequiredMixin, generic.DetailView):
    model=Form
    template_name = 'forms/view-form-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
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

#new form stuff
class CreateForm(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'forms/create-form-all.html', 
                          { 'form': FormsForm(organization=request.user.userprofile.organization), 'form_question':FormQuestionForm(),
                           'msg':'Double check that all the fields are correctly filled out.' })

    def post(self, request):
        form = Form(
            form_name = request.POST.get('form_name'),
            organization = get_object_or_404(Organization, id=request.POST.get('organization')),
            start_date = request.POST.get('start_date'),
            end_date = request.POST.get('end_date'),
            )
        form.save()
        questionValues = request.POST.getlist('question')
        qLogicValues = request.POST.getlist('visible_if_question')
        aLogicValues = request.POST.getlist('visible_if_answer')
        for i in range(len(questionValues)):
            if qLogicValues[i] != '':
                formQ = FormQuestion(
                    form=form,
                    index = i,
                    question = get_object_or_404(Question, id=questionValues[i]),
                    visible_if_question = get_object_or_404(Question, id=qLogicValues[i]),
                    visible_if_answer = aLogicValues[i]
                    )
            else:
                formQ = FormQuestion(
                    form=form,
                    index = i,
                    question = get_object_or_404(Question, id=questionValues[i]),
                    visible_if_question = None,
                    visible_if_answer = None
                    )
            formQ.save()

        return HttpResponseRedirect(reverse('forms:view-form-detail', kwargs={'pk': form.id}))


class UpdateForm(LoginRequiredMixin, View):
    def get(self, request, pk):
        form = get_object_or_404(Form, id=pk)
        formQs = FormQuestion.objects.filter(form = form.id)
        print(formQs)
        formQForms = [FormQuestionForm(instance=fq) for fq in formQs]
        return render(request, 'forms/update-form-all.html', 
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

        questionValues = request.POST.getlist('question')
        qLogicValues = request.POST.getlist('visible_if_question')
        aLogicValues = request.POST.getlist('visible_if_answer')

        existingQuestions = FormQuestion.objects.filter(form=form.id)
        if len(existingQuestions) > len(questionValues):
            for extra in existingQuestions[len(questionValues):]:
                extra.delete()

        for i in range(len(questionValues)):
            if i+1 <= len(existingQuestions):
                formQ = existingQuestions[i]
                if qLogicValues[i] != '':
                    formQ.index = i
                    formQ.question = get_object_or_404(Question, id=questionValues[i])
                    formQ.visible_if_question = get_object_or_404(Question, id=qLogicValues[i])
                    formQ.visible_if_answer = aLogicValues[i]
                else:
                    formQ.index = i
                    formQ.question = get_object_or_404(Question, id=questionValues[i])
                    formQ.visible_if_question = None
                    formQ.visible_if_answer = None
            else:
                if qLogicValues[i] != '':
                    formQ = FormQuestion(
                        form=form,
                        index = i,
                        question = get_object_or_404(Question, id=questionValues[i]),
                        visible_if_question = get_object_or_404(Question, id=qLogicValues[i]),
                        visible_if_answer = aLogicValues[i]
                        )
                else:
                    formQ = FormQuestion(
                        form=form,
                        index = i,
                        question = get_object_or_404(Question, id=questionValues[i]),
                        visible_if_question = None,
                        visible_if_answer = None
                        )
            formQ.save()
        return HttpResponseRedirect(reverse('forms:view-form-detail', kwargs={'pk': form.id}))
    
class DeleteForm(LoginRequiredMixin, generic.DeleteView):
    model=Form
    success_url = reverse_lazy('forms:view-forms-index')

#questions are meant to be modular, and as such are edited separately from forms
class CreateQuestion(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'forms/create-question.html', 
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
            return JsonResponse({'redirect': reverse('forms:view-forms-index')})
        except:
            print('Ah nuts')

class UpdateQuestion(LoginRequiredMixin, View):
    def get(self, request, pk):
        question = get_object_or_404(Question, id=pk)
        options = Option.objects.filter(question=question.id)
        return render(request, 'forms/update-question.html', 
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
            return JsonResponse({'redirect': reverse('forms:view-forms-index')})
        except:
            print('Ah nuts')


class DeleteQuestion(LoginRequiredMixin, generic.DeleteView):
    model=Question
    def get_success_url(self):
        return reverse_lazy('forms:view-forms-index')




#views related to responses
class ViewResponseIndex(LoginRequiredMixin, generic.ListView):
    model=Response
    template_name='forms/view-responses-index.html'
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
        user_org = self.request.user.userprofile.organization
        return render(request, 'forms/create-response.html', 
                    { 'form': ResponseForm(formQs=self.form_questions, formLogic=self.form_structure),
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
            return render(request, 'forms/create-response.html', 
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
        return render(request, 'forms/update-response.html', 
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
        user_org = self.request.user.userprofile.organization
        respondent = self.get_object()
        responses = Response.objects.filter(respondent=respondent).order_by('response_date')
        context['respondent'] = respondent
        context['responses'] = responses
        context['user_org'] = user_org
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
    success_url = reverse_lazy('forms:view-respondents-index')

    #logic for instance where respondent has responses would go here


class ViewOrgsIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/view-orgs-index.html'
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
    template_name='forms/view-org-detail.html'
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
    template_name = 'forms/update-org.html'
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
    template_name = 'forms/update-org.html'
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