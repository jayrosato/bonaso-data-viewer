from django import forms
from django.forms import ModelForm
from django.forms import inlineformset_factory
from django.db.models import Q
from django.forms.widgets import CheckboxSelectMultiple

from .models import Respondent, Question, Option, FormQuestion, Form, Answer, User

class DateInput(forms.DateInput):
    input_type = 'date'

class SelectRespondentForm(forms.Form):
    respondent = forms.ModelChoiceField(queryset=Respondent.objects.all(),label='Respondent')

class RespondentForm(ModelForm):
    class Meta:
        model=Respondent
        fields = [
            'id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship', 'ward', 'village', 
            'district', 'email', 'contact_no', 'created_by'
            ]
        widgets = {
            'dob': DateInput()
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['created_by'].queryset = User.objects.filter(id=user.id)
        self.fields['created_by'].initial = User.objects.filter(id=user.id)

class DynamicCheckboxes(CheckboxSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)

        if hasattr(value, 'instance') and hasattr(value.instance, 'special'):
            special_value = value.instance.special
            option['attrs']['data-special'] = special_value
        return option
    
class ResponseForm(forms.Form):
    def __init__(self, *args, formQuestions, response=None, **kwargs):
        super().__init__(*args, **kwargs)
        CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ]
        if response == None:
            self.fields['Respondent'] = forms.ModelChoiceField(queryset=Respondent.objects.all())

        for fq in formQuestions:
            field = fq.id
            question = fq.question
            if response:
                if question.question_type == 'Multiple Selections':
                    answer = Answer.objects.filter(response=response, question=question)
                else:
                    answer = Answer.objects.filter(response=response, question=question).first()
            else:
                answer = None
            if question.question_type == 'Text':
                self.fields[field] = forms.CharField(max_length=100000)
                if answer:
                    self.fields[field].initial = answer.open_answer
            if question.question_type == 'Number':
                self.fields[field] = forms.CharField(max_length=100)
                self.fields[field].widget.attrs.update({'number':'yes'})
                if answer:
                    self.fields[field].initial = answer.open_answer
            if question.question_type == 'Yes/No':
                self.fields[field] = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
                if answer:
                    self.fields[field].initial = answer.open_answer

            if question.question_type == 'Single Selection':
                self.fields[field] = forms.ModelChoiceField(queryset=Option.objects.filter(pk__in=question.option_set.all()), widget=forms.RadioSelect)
                if answer:
                    self.fields[field].initial = answer.option
           
            if question.question_type == 'Multiple Selections':
                self.fields[field] = forms.ModelMultipleChoiceField(queryset=Option.objects.filter(pk__in=question.option_set.all()), widget=DynamicCheckboxes)
                if answer:
                    options = [a.option for a in answer]
                    self.fields[field].initial = options
                    if len(options) == len(Option.objects.filter(question=question, special=None)):
                        special = Option.objects.filter(question=question, special='All').first()
                        if special:
                            self.fields[field].initial = special
                if not answer:
                    special = Option.objects.filter(question=question, special='None of the above').first()
                    if special:
                        self.fields[field].initial = special
            self.fields[field].label = question.question_text
            self.fields[field].widget.attrs.update({'class':'form_question'})
            self.fields[field].widget.attrs.update({'fqID':fq.id})
            self.fields[field].required = False

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
        widgets = {
            'start_date': DateInput(), 'end_date':DateInput(),
        }
    def __init__(self, *args, userProfile, **kwargs):
        super().__init__(*args, **kwargs)
        from organizations.models import Organization
        userOrg = userProfile.organization
        if userProfile.access_level != 'admin':
            self.fields['organization'].queryset = Organization.objects.filter(Q(id=userOrg.id) | Q(parent_organization=userOrg.id))
            self.fields['organization'].initial = userOrg.id

class FormQuestionForm(forms.ModelForm):
    class Meta:
        model = FormQuestion
        fields = [
            'question'
        ]
    widgets = {
            'id': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['fqID'] = forms.IntegerField(widget=forms.HiddenInput(), initial=self.instance.pk)

class QuestionSelector(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['question']


