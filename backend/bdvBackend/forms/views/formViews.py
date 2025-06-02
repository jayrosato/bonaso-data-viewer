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

from forms.forms import FormsForm
from forms.models import Form, FormQuestion, Question, Option, Response, FormLogic, FormLogicRule


class ViewFormsIndex(LoginRequiredMixin, generic.ListView):
    #index view for seeing a list of forms. By default is limited to forms from a users organization and active forms
    template_name = 'forms/forms/view-forms-index.html'
    context_object_name = 'active_forms'
    
    def get_queryset(self):
        user_org = self.request.user.userprofile.organization
        today = date.today()
        return Form.objects.filter(organization = user_org, start_date__lte = today, end_date__gte = today)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        context['active'] = True
        return context

class ViewPastForms(LoginRequiredMixin, generic.ListView):
    #index view for seeing a list of forms. By default is limited to forms from a users organization and active forms
    template_name = 'forms/forms/view-forms-index.html'
    context_object_name = 'active_forms'
    
    def get_queryset(self):
        user_org = self.request.user.userprofile.organization
        today = date.today()
        return Form.objects.filter(organization = user_org)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        context['active'] = False
        return context

class ViewFormDetail(LoginRequiredMixin, generic.DetailView):
    #view
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

class CreateUpdateForm(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        if pk:
            form = Form.objects.filter(id=pk).first()
            return render(request, 'forms/forms/update-form-all.html',
                        {'form': FormsForm(userProfile = request.user.userprofile, instance=form), 
                          'form_meta': form, 
                          'user_org':request.user.userprofile.organization})
        else:
            return render(request, 'forms/forms/update-form-all.html', 
                          {'form': FormsForm(userProfile = request.user.userprofile),
                           'form_meta': None,
                            'user_org':request.user.userprofile.organization})
    def post(self, request, pk=None):
        from organizations.models import Organization
        data = json.loads(request.body)

        if len(data['form_questions']) == 0:
            return JsonResponse({'warning': 'Form has no questions!'})
        
        print(data)
        if pk:
            form = Form.objects.filter(id=pk).first()
        else:
            form = Form()
        form.form_name = data['form_name']
        if not data['organization'].isnumeric():
            return JsonResponse({'warning': 'Organization was invalid. Please double check this selection.'})

        organization = Organization.objects.filter(id=data['organization']).first()
        form.organization = organization
        form.start_date = data['start_date']
        form.end_date = data['end_date']
        form.save()

        uploadedQuestions = data['form_questions']
        existingQuestions = FormQuestion.objects.filter(form=form.id)
        print(uploadedQuestions)
        print(existingQuestions)
        for eq in existingQuestions:
            if not eq.id in uploadedQuestions:
                eq.delete()

        for fq in data['form_questions']:
            fqID = fq['id']
            if fqID:
                if not fqID.isnumeric():
                    return JsonResponse({'warning': f'Question at {fq['index']+1} sent an invalid value. Please double check this field.'})
                checkFQ = FormQuestion.objects.filter(id=fqID).first()
                if checkFQ:
                    formQuestion = checkFQ
                else:
                    formQuestion = FormQuestion()
            else:
                formQuestion = FormQuestion()
            if not fq['question'].isnumeric():
                return JsonResponse({'warning': f'Question at {fq['index']+1} sent an invalid value. Please double check this field.'})
            question = Question.objects.filter(id=fq['question']).first()
            formQuestion.form = form
            formQuestion.question = question
            formQuestion.index = fq['index']

            formQuestion.save()
            if fq['logic']:
                logic = fq['logic']
                rules = logic['rules']
                if not rules or len(rules)== 0:
                    return JsonResponse({'warning': f'Question at index {fq['index']+1} has logic, but no rules!'})
                if fqID:
                    checkLogic = FormLogic.objects.filter(conditional_question = fqID).first()
                    if checkLogic:
                        formLogic = checkLogic
                        existingRules = FormLogicRule.objects.filter(form_logic = formLogic.id)
                        for rule in existingRules:
                            rule.delete()
                    else:
                        formLogic = FormLogic()
                else:
                    formLogic = FormLogic()
                formLogic.form = form
                formLogic.conditional_question = formQuestion
                formLogic.conditional_operator = logic['conditional_operator']
                formLogic.on_match = 'Show'
                formLogic.save()
                for rule in rules:
                    formLogicRule = FormLogicRule()
                    if not rule['parent_question'].isnumeric():
                        return JsonResponse({'warning': f"A rule's parent question at question{fq['index']+1} sent an invalid value. Please double check this field."})
                    parentQuestion = FormQuestion.objects.filter(form=form.id, question=rule['parent_question']).first()
                    formLogicRule.form_logic = formLogic
                    formLogicRule.parent_question = parentQuestion
                    formLogicRule.expected_values = rule['expected_value']
                    formLogicRule.value_comparison = rule['value_comparison']
                    formLogicRule.limit_options = rule['limit_options']
                    formLogicRule.negate_value = rule['negate_value']
                    formLogicRule.save()
        return JsonResponse({'redirect': reverse('forms:view-form-detail', kwargs={'pk': form.id})})

class DuplicateForm(LoginRequiredMixin, View):
    def post(self, request, pk):
        copyForm = Form.objects.filter(id=pk).first()
        oldID = copyForm.id
        copyForm.pk = None
        copyForm.form_name = 'Copy of ' + copyForm.form_name
        copyForm.save()

        copyFQs = FormQuestion.objects.filter(form=oldID)
        oldFQs = []
        for fq in copyFQs:
            oldFQ = fq.id
            newFQ = fq
            newFQ.pk = None
            newFQ.form = copyForm
            newFQ.save()

            checkLogic = FormLogic.objects.filter(conditional_question = oldFQ).first()
            if checkLogic:
                oldLogic = checkLogic.id
                newLogic = checkLogic
                newLogic.pk = None
                newLogic.form = copyForm
                newLogic.conditional_question = newFQ
                newLogic.save()
                checkRules = FormLogicRule.objects.filter(form_logic = oldLogic)
                if checkRules:
                    for rule in checkRules:
                        oldRule = rule.id
                        newRule = rule
                        newRule.pk = None
                        newRule.form_logic = newLogic
                        newRule.save()
            oldFQs.append({'newFQ': newFQ, 'oldFQ':oldFQ})

        for fq in oldFQs:
            checkDepRules = FormLogicRule.objects.filter(form_logic = newLogic, parent_question = fq['oldFQ'])
            if checkDepRules:
                for rule in checkDepRules:
                    rule.parent_question = fq['newFQ']
                    rule.save()
        return HttpResponseRedirect(reverse('forms:view-form-detail', kwargs={'pk': copyForm.id}))
    
class DeleteForm(LoginRequiredMixin, generic.DeleteView):
    model=Form
    success_url = reverse_lazy('forms:view-forms-index')