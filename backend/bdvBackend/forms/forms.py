from django import forms
from django.forms import ModelForm
from django.forms import inlineformset_factory
from django.db.models import Q
from .models import Respondent, Question, Option, FormQuestion, Organization, Form, Answer

class SelectRespondentForm(forms.Form):
    respondent = forms.ModelChoiceField(queryset=Respondent.objects.all(),label='Respondent')

class RespondentForm(ModelForm):
    class Meta:
        model=Respondent
        fields = [
            'id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship', 'ward', 'village', 
            'district', 'email', 'contact_no'
            ] 

class ResponseForm(forms.Form):
    def __init__(self, *args, formQs, formLogic, response=None, **kwargs):
        super().__init__(*args, **kwargs)
        CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ]
        self.formQs = formQs
        if response == None:
            field_name = 'Respondent'
            self.fields[field_name] = forms.ModelChoiceField(queryset=Respondent.objects.all())
        else: 
            self.response=response

        for i in range(len(formQs)):
            field_name = formQs[i].question_text
            if formQs[i].question_type == 'Text':
                self.fields[field_name] = forms.CharField(max_length=100000)
                if response:
                    self.fields[field_name].initial = Answer.objects.filter(response=self.response.id, question=formQs[i].id).first().open_answer
            if formQs[i].question_type == 'Number':
                self.fields[field_name] = forms.NumberInput()
                if response:
                    self.fields[field_name].initial = Answer.objects.filter(response=self.response.id, question=formQs[i].id).first().open_answer
            if formQs[i].question_type == 'Yes/No':
                self.fields[field_name] = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
                if response:
                    self.fields[field_name].initial = Answer.objects.filter(response=self.response.id, question=formQs[i].id).first().open_answer

            if formQs[i].question_type == 'Single Selection':
                self.fields[field_name] = forms.ModelChoiceField(queryset=Option.objects.filter(pk__in=formQs[i].option_set.all()), widget=forms.RadioSelect)
                if response:
                    try:
                        self.fields[field_name].initial = Answer.objects.filter(response=self.response.id, question=formQs[i].id).first().option
                    except:
                        continue
           
            if formQs[i].question_type == 'Multiple Selections':
                self.fields[field_name] = forms.ModelMultipleChoiceField(queryset=Option.objects.filter(pk__in=formQs[i].option_set.all()), widget=forms.CheckboxSelectMultiple)
                if response:
                    answers = Answer.objects.filter(response=self.response.id, question=formQs[i].id)
                    options = [a.option for a in answers]
                    self.fields[field_name].initial = options
            
            self.fields[field_name].widget.attrs.update({'class':'form_question'})

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'question_text', 'question_type'
        ]

class FormsForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = [
            'form_name', 'organization', 'start_date', 'end_date'
        ]
    def __init__(self, *args, organization, **kwargs):
        super().__init__(*args, **kwargs)
        if organization.id != 3:
            self.fields['organization'].queryset = Organization.objects.filter(Q(id=organization.id) | Q(parent_organization=organization.id))
            self.fields['organization'].initial = organization.id

class FormQuestionForm(forms.ModelForm):
    class Meta:
        model = FormQuestion
        fields = [
            'question'
        ]

class QuestionSelector(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['question']