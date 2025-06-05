from django.views import View
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
User = get_user_model()
from accounts.models import UserProfile

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from django.contrib import messages

from datetime import datetime, date
from django.utils import timezone
import re
from email_validator import validate_email, EmailNotValidError
from pathlib import Path
import csv

from forms.forms import ResponseForm, QuestionForm, FormsForm, FormQuestionForm, QuestionSelector, RespondentForm
from forms.models import Respondent, Form, FormQuestion, Question, Option, Response, Answer, FormLogic, FormLogicRule

now = timezone.now()

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
        respondent_fields.remove('created_by')
        question_fields = [q.question_text for q in form_questions]

        fields = respondent_fields + ['response_date'] + question_fields
        writer = csv.writer(response)
        writer.writerow(fields)

        return response

    def post(self, request, pk):
        override = False #by default, leave any existing users alone
        form_meta = get_object_or_404(Form, id=pk)
        form_structure = FormQuestion.objects.filter(form=form_meta).order_by('index')
        form_questions = [fq.question for fq in form_structure]
        if form_questions:
            try:
                if request.POST['template'] == '':
                    messages.add_message(request, messages.INFO, 'Uploaded file must be a .csv file.')
                    return HttpResponseRedirect(reverse("forms:view-form-detail", kwargs={'pk': form_meta.id}))
            except:
                pass
            csv_file = request.FILES['template']
            testFile = str(csv_file)
            file_extension = Path(testFile).suffix
            if file_extension != '.csv':
                messages.add_message(request, messages.INFO, 'Uploaded file must be a .csv file.')
                return HttpResponseRedirect(reverse("forms:view-form-detail", kwargs={'pk': form_meta.id}))
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for index, row in enumerate(reader):
                #see if respondent already exists
                checkRespondent = Respondent.objects.filter(id_no=row['id_no']).first()
                if not checkRespondent:
                    respondent = Respondent(id_no=row['id_no'])
                    override = True
                else:
                    respondent = checkRespondent

                if override:
                    #check if DOB is valid
                    raw_date = row['dob'].strip().replace('“', '').replace('”', '').replace('"', '')
                    try:
                        parsed_date = datetime.strptime(raw_date, '%m/%d/%Y').date()
                    except ValueError:
                        messages.add_message(request, messages.INFO, f'Row {index+1} contains an invalid date value (expected MM/DD/YY) at column Date of Birth. This response will not be recorded until the error is fixed.')
                        continue
                    if parsed_date > datetime.today().date():
                        messages.add_message(request, messages.INFO, f'Row {index+1} contains an impossible date of birth. Please verify this record.')
                    #check for valid sex responses
                    maleResponses = ['m', 'male', 'man', 'boy']
                    femaleResponses = ['f', 'female', 'woman', 'girl']
                    nbResponses = ['nb', 'non-binary', 'nonbinary', ]
                    sex =  row['sex'].replace(' ', '').lower()
                    if sex in maleResponses:
                        sex = 'M'
                    elif sex in femaleResponses:
                        sex = 'F'
                    elif sex in nbResponses:
                        sex = 'NB'
                    else:
                        messages.add_message(request, messages.INFO, f'Respondent sex at row {index+1} contained a value we could not read. Please enter "male/female/non-binary" or "M/F/NB".')
                        continue

                    #check email (if provided)
                    if row['email'] != '':
                        try:
                            emailInfo = validate_email(row['email'], check_deliverability=False)
                            email = emailInfo.normalized

                        except EmailNotValidError as e:
                            email = ''
                            messages.add_message(request, messages.INFO, f'Respondent email at row {index+1} contained an invalid email address. Value was not recorded.')
                    else:
                        email = None
                    if row['contact_no'] != '':
                        checkNum = re.search(r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$', row['contact_no'])
                        if not checkNum:
                            num = None
                            messages.add_message(request, messages.INFO, f'Respondent email at row {index+1} contained an invalid phone number. Value was not recorded.')
                        else:
                            num = row['contact_no']
                    
                    if override:
                        respondent.fname = row['fname']
                        respondent.lname = row['lname']
                        respondent.dob = parsed_date
                        respondent.sex = sex
                        respondent.ward = row['ward']
                        respondent.village = row['village']
                        respondent.district = row['district']
                        respondent.citizenship = row['citizenship']
                        respondent.email = email
                        respondent.contact_no = num
                        respondent.save()

                #check/create a new response
                checkResponse = Response.objects.filter(form = form_meta.id, respondent = respondent.id).first()
                if checkResponse:
                    response = checkResponse
                    response.updated_at = now
                else:
                    response = Response(respondent=respondent, form=form_meta, created_by=request.user, response_date = responseDate)

                raw_date = row['response_date'].strip().replace('“', '').replace('”', '').replace('"', '')
                try:
                    responseDate = datetime.strptime(raw_date, '%m/%d/%Y')
                except ValueError:
                    messages.add_message(request, messages.INFO, f'Row {index+1} contains an invalid date value (expected MM/DD/YY) at column Response Date. This response will default to the current date until the error is fixed.')
                    responseDate = datetime.today()
                if responseDate.date() > form_meta.end_date or responseDate.date() < form_meta.start_date:
                    messages.add_message(request, messages.INFO, f'Row {index+1} contains a response date that is outside the time period of this form. Please double check this value.')
                    response.flag = True
                response.response_date = responseDate

                response.save()
                
                for i in range(len(form_questions)):
                    #check for an existing answer and fetch it if it exists
                    if checkResponse:
                        checkAnswer = Answer.objects.filter(response = response, question = form_questions[i])
                        if checkAnswer and form_questions[i].question_type != 'Multiple Selections': 
                            answer = checkAnswer.first()
                        #to avoid confusion, if there are multiple answers just remove them
                        elif checkAnswer and form_questions[i].question_type == 'Multiple Selections':
                            for a in checkAnswer:
                                a.delete()
                    #if not an existing answer or if the response is new, create a new answer object
                        else:
                            answer = Answer(response = response, question = form_questions[i])
                    else:
                        answer = Answer(response = response, question = form_questions[i])

                    if form_questions[i].question_type == 'Text' or form_questions[i].question_type == 'Number':
                        openResponse = row[form_questions[i].question_text]
                        if form_questions[i].question_type == 'Number':
                            if openResponse == '':
                                openResponse = 0
                                messages.add_message(request, messages.INFO, f'The answer at column {i+13} row {index+1} contained an blank entry. This has been recorded as 0. If this was not intentional, please add a valid number.')
                            try:
                                float(openResponse)
                            except (TypeError, ValueError):
                                messages.add_message(request, messages.INFO, f'Answer "{row[form_questions[i].question_text]}" at column {i+13} row {index+1} expected a number.')
                                continue
                        answer.open_answer=openResponse
                        answer.save()
                    if form_questions[i].question_type == 'Yes/No':
                        yesNo = row[form_questions[i].question_text]
                        if yesNo.strip().lower() == 'yes':
                            yesNo = 'Yes'
                        elif yesNo.strip().lower() == 'no':
                            yesNo = 'No'
                        else:
                            messages.add_message(request, messages.INFO, f'Answer "{row[form_questions[i].question_text]}" at column {i+13} row {index+1} is not a valid response. This question requires either a "Yes" or a "No"')
                            continue
                        answer.open_answer = yesNo
                        answer.save()

                    if form_questions[i].question_type == 'Single Selection':
                        notFound = False
                        value = row[form_questions[i].question_text].strip().lower()
                        try:
                            int(value)
                            checkOption = Option.objects.filter(id = value)
                            if checkOption:
                                answer.option =checkOption
                            else:
                                notFound = True
                        except (TypeError, ValueError):
                            notFound = True
                        if notFound:  
                            checkOption = Option.objects.filter(option_text__iexact=value, question=form_questions[i].id).first()
                            if checkOption:
                                answer.option = checkOption
                            else:
                                messages.add_message(request, messages.INFO, f'Answer "{row[form_questions[i].question_text]}" at column {i+13} row {index+1} is not a valid response. No response will be recorded. Please double check that this is a valid response for this question.')
                                continue
                        answer.save()

                    if form_questions[i].question_type == 'Multiple Selections':
                        selected_options = row[form_questions[i].question_text].split(',')
                        for o in range(len(selected_options)):
                            value = selected_options[o].strip().lower()
                            try:
                                int(value)
                                checkOption = Option.objects.filter(id = value)
                                if checkOption:
                                    answer = Answer(response=response, question = form_questions[i], option = checkOption)
                                else:
                                    notFound = True
                            except (TypeError, ValueError):
                                notFound = True
                            if notFound:  
                                checkOption = Option.objects.filter(option_text__iexact=value, question=form_questions[i].id).first()
                                if checkOption:
                                    answer = Answer(response=response, question = form_questions[i], option = checkOption)
                                else:
                                    messages.add_message(request, messages.INFO, f'Answer "{row[form_questions[i].question_text]}" at column {i+13} row {index+1} is not a valid response. No response will be recorded. Please double check that this is a valid response for this question.')
                                    continue
                            answer.save()
        return HttpResponseRedirect(reverse("forms:view-form-detail", kwargs={'pk': form_meta.id}))