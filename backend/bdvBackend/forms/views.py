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

from .forms import ResponseForm, QuestionForm, FormsForm, FormQuestionForm, QuestionSelector
from datetime import datetime

import csv
from django.db.models import Q, Count

from.models import Respondent, Form, FormQuestion, Question, Option, Response, Answer, Organization
now = timezone.now()

#views related to forms
class ViewFormsIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/forms/view-forms-index.html'
    context_object_name = 'active_forms'
    
    def get_queryset(self):
        num_visits = self.request.session.get('num_visits',0)
        num_visits += 1
        self.request.session['num_visits'] = num_visits
        last_login = self.request.session.get('last_login', 0)
        last_login = now.isoformat()
        self.request.session['last_login'] = last_login
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
        return render(request, 'forms/forms/create-form-all.html', 
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
            return JsonResponse({'redirect': reverse('forms:view-forms-index')})
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
            'district', 'email', 'contact_no'
            ]
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

    #logic for instance where respondent has responses would go here


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

class GetDataQ(LoginRequiredMixin, View):
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
                if not checkRespondent:
                    raw_date = row['dob'].strip().replace('“', '').replace('”', '').replace('"', '')
                    try:
                        parsed_date = datetime.strptime(raw_date, '%m/%d/%Y').date()
                    except ValueError:
                        raise ValueError(f"Invalid date format: {raw_date}. Expected MM/DD/YYYY.")
                    respondent = Respondent(id_no=row['id_no'], fname=row['fname'], lname=row['lname'], dob=parsed_date, sex=row['sex'], ward=row['ward'], village=row['village'], district=row['district'], citizenship=row['citizenship'], email=row['email'], contact_no=row['contact_no'])
                    respondent.save()
                else:
                    respondent = checkRespondent
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
                            answer = Answer(response=response, question=form_questions[i],  option=get_object_or_404(Option, pk=selected_options[o]), open_answer=None)
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
                