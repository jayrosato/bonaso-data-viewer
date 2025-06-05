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
import json
from django.utils import timezone
from datetime import datetime, date


from forms.models import Respondent, Form, FormQuestion, Question, Option, Response, Answer, FormLogic, FormLogicRule

#used for getting form information, either for editing a form of for utilizing form logic
class GetFormInfo(LoginRequiredMixin, View):
    def get(self, request, pk):
        formQuestions = FormQuestion.objects.filter(form=pk).order_by('index')
        form_logic = FormLogic.objects.filter()
        logic_rules = FormLogicRule.objects.all().select_related('form_logic')
        logic_map = {
            logic.conditional_question.id: {
                'id': logic.id,
                'conditional_operator': logic.conditional_operator,
                'rules': []
            }
            for logic in form_logic
        }
        for rule in logic_rules:
            logic_id = rule.form_logic_id
            for logic in form_logic:
                if logic.id == logic_id:
                    conditional_question_id = logic.conditional_question_id
                    logic_map[conditional_question_id]['rules'].append({
                                    'id': rule.id,
                                    'parent_question_id': rule.parent_question.question_id,
                                    'parent_question': rule.parent_question_id,
                                    'expected_values': rule.expected_values,
                                    'value_comparison': rule.value_comparison,
                                    'negate_value': rule.negate_value,
                                    'limit_options': rule.limit_options,
                    })
        data = []
        for fq in formQuestions:
            question=fq.question
            fq_data= {
                'id': fq.id,
                    'index': fq.index,
                    'question_id':question.id,
                    'question': question.question_text,
                    'question_type':question.question_type,
                    'options':[
                        {
                            'id': option.id,
                            'option_text': option.option_text,
                            'special': option.special
                        } for option in question.option_set.all()
                    ]
            }
            if fq.id in logic_map:
                fq_data['logic'] = logic_map[fq.id]

            data.append(fq_data)
        return JsonResponse(data, safe=False)

class GetQuestions(LoginRequiredMixin, View):
    def get(self, request):
        questions = Question.objects.all()
        data = {
            'labels':[q.question_text for q in questions],
            'ids':[q.id for q in questions],
            'types':[q.question_type for q in questions],
        }
        return JsonResponse(data)

class GetQuestionResponses(LoginRequiredMixin, View):
    def get(self, request):
        from organizations.models import Organization
        allAnswers = Answer.objects.all().select_related(
            'option',
            'response__form__organization',
            'response__respondent',
            'question'
        )
        questionMap = {}
        for answer in allAnswers:
            question = answer.question
            if question.id not in questionMap:
                questionMap[question.id] = {
                    'question_id': question.id,
                    'question_text': question.question_text,
                    'answers': [],
                    'question_type': question.question_type
                }
            response = answer.response
            if question.question_type in ['Single Selection', 'Multiple Selections']:
                value = answer.option.option_text if answer.option else None
            else:
                value = answer.open_answer
            questionMap[question.id]['answers'].append({
                'answer_id': answer.id,
                'answer_value': value,
                'date': response.response_date,
                'respondent_id': response.respondent.id,
                'sex': response.respondent.sex,
                'age': response.respondent.get_age(),
                'district': response.respondent.district,
                'organization': response.form.organization.id,
                'organization_name': response.form.organization.organization_name
            })
        sexValues = list(set(list(Respondent.objects.values_list('sex', flat=True))))
        districtValues = list(set(list(Respondent.objects.values_list('district', flat=True))))
        orgNames = list(set(list(Organization.objects.values_list('organization_name', flat=True).order_by('id'))))
        orgValues = list(set(list(Organization.objects.values_list('id', flat=True).order_by('id'))))

        filters = [
            {'name': 'date', 'type': 'date'},
            {'name': 'sex', 'type': 'multiple', 'values':sexValues},
            {'name': 'age', 'type': 'number'},
            {'name': 'district', 'type': 'multiple', 'values':districtValues},
            {'name': 'organization', 'type': 'multiple', 'values':orgValues, 'labels':orgNames}
        ]

        data = {'questions': [],'filters': filters}
        for q in questionMap.values():
            data['questions'].append(q)

        return JsonResponse(data, safe=False) 


#used to get information about question options/logic when editing forms
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