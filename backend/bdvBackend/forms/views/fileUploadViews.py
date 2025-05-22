from django.views import View
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
User = get_user_model()
from accounts.models import UserProfile

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from datetime import datetime, date
from django.utils import timezone
import csv

from forms.forms import ResponseForm, QuestionForm, FormsForm, FormQuestionForm, QuestionSelector, RespondentForm
from forms.models import Respondent, Form, FormQuestion, Question, Option, Response, Answer, FormLogic, FormLogicRule


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