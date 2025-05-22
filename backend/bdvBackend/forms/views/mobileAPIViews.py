from django.views import generic, View
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

from rest_framework.views import APIView
from rest_framework.response import Response as APIResponse
from rest_framework import status, permissions

from forms.models import Respondent, Form, FormQuestion, Question, Option, Response, Answer, FormLogic, FormLogicRule


class GetForms(APIView):
    def get(self, request, pk):
        user = User.objects.filter(id=pk).first()
        userProfile = UserProfile.objects.filter(user = user).first()
        userOrg = userProfile.organization
        today = date.today()
        #filter is_active && filter by organization --> once accounts are set up
        forms = Form.objects.filter(organization = userOrg, start_date__lte = today, end_date__gte = today).select_related('organization').prefetch_related('formquestion_set__question__option_set')
        form_logic = FormLogic.objects.all().select_related('conditional_question')
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
                                    'parent_question': rule.parent_question_id,
                                    'expected_values': rule.expected_values,
                                    'value_comparison': rule.value_comparison,
                                    'negate_value': rule.negate_value,
                                    'limit_options': rule.limit_options,
                    })
        data = []
        for form in forms:
            form_data = {
                'id': form.id,
                'form_name': form.form_name,
                'organization':{
                    'organization_id': form.organization.id,
                    'organization_name': form.organization.organization_name
                },
                'start_date': form.start_date,
                'end_date': form.end_date,
                'form_questions': []
            }

            for fq in form.formquestion_set.all():
                question=fq.question
                fq_data= {
                    'id': fq.id,
                        'index': fq.index,
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

                form_data['form_questions'].append(fq_data)

            data.append(form_data)
        return JsonResponse(data, safe=False)


class SyncMobileResponses(APIView):
    def post(self, request):
        data= json.loads(request.body)
        data=data['data']
        print(data)
        respondents = data['respondents']
        respRef = {}
        responses = data['responses']
        for resp in respondents:
            respondent = None
            if resp['linked_id']:
                respondent = Respondent.objects.filter(id=resp['linked_id']).first()
            else:
                respondent = Respondent.objects.filter(id_no=resp['id_no']).first()
            if not respondent:
                respondent = Respondent(id_no = resp['id_no'])
            if not resp['created_by']:
                created_by = User.objects.filter(id=1).first()
            else:
                created_by = User.objects.filter(id=resp['created_by'])
            respondent.fname = resp['fname']
            respondent.lname = resp['lname']
            respondent.sex = resp['sex']
            respondent.dob = resp['dob']
            respondent.ward = resp['ward']
            respondent.village = resp['village']
            respondent.district = resp['district']
            respondent.citizenship = resp['citizenship']
            respondent.contact_no = resp['contact_no']
            respondent.email = resp['email']
            respondent.created_by = created_by
            respondent.save()
            respRef[resp['id']] = respondent.id #ids in the django database will probably never line up with ids from local storage (both are autoincrement), so put this reference here
        for r in responses:
            respondentID = respRef[r['respondent']]
            respondent = get_object_or_404(Respondent, id=respondentID)
            form = Form.objects.filter(id=r['form']).first()
            response = Response.objects.filter(form=form.id, respondent = respondentID).first()
            created_by = User.objects.filter(id=r['created_by']).first()
            if not response:
                response = Response(form=form, respondent=respondent, created_by=created_by, response_date=r['created_on'])
            else:
                response.updated_at = timezone.now()
            response.save()
            clearedQuestions = []
            for a in r['answers']:
                fqToQ = int(a['question'])
                fqToQ = FormQuestion.objects.filter(id=fqToQ).first()
                question = fqToQ.question
                print(clearedQuestions)
                answer=None
                if question.question_type == 'Multiple Selections' and question.id not in clearedQuestions:
                    print('running for question', question.id)
                    existingAnswers = Answer.objects.filter(question=question.id, response=response.id)
                    for ea in existingAnswers:
                        ea.delete()
                    clearedQuestions.append(question.id)
                elif question.question_type != 'Multiple Selections':
                    answer = Answer.objects.filter(question=question.id, response=response.id).first()
                if not answer:
                    answer = Answer(question=question, response = response)
                if a['option']:
                    option = Option.objects.filter(id=a['option']).first()
                    if option.special == 'None of the above':
                        continue
                    elif option.special == 'All':
                        options = Option.objects.filter(question = question.id)
                        for option in options:
                            if not option.special:
                                answer = Answer(response=response, question=question,  option=option, open_answer=None)
                                answer.save()
                        continue
                    else:
                        answer.option = option
                elif a['open_answer']:
                    answer.open_answer = a['open_answer']
                answer.save()
        print('Responses synced!')
        return APIResponse({"message": "success"}, status=status.HTTP_200_OK)