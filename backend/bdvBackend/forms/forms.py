from django import forms
from django.forms import ModelForm

from .models import Respondent, Question, Option, FormQuestion

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
    def __init__(self, *args, formQs, formLogic, **kwargs):
        super().__init__(*args, **kwargs)
        CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        ]
        self.formQs = formQs
        field_name = 'Respondent'
        self.fields[field_name] = forms.ModelChoiceField(queryset=Respondent.objects.all())
        for i in range(len(formQs)):
            '''
            if formLogic:
                conditions = formLogic[i]
                print(conditions)
                if(conditions.visible_if_question):
                    if self.data.get(conditions.visible_if_question) != conditions.visible_if_question:
                        continue
            '''
            field_name = formQs[i].question_text
            if formQs[i].question_type == 'Text':
                self.fields[field_name] = forms.CharField(max_length=100000)
            if formQs[i].question_type == 'Number':
                self.fields[field_name] = forms.NumberInput()
            if formQs[i].question_type == 'Yes/No':
                self.fields[field_name] = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
            if formQs[i].question_type == 'Single Selection':
                self.fields[field_name] = forms.ModelChoiceField(queryset=Option.objects.filter(pk__in=formQs[i].option_set.all()), widget=forms.RadioSelect)
            if formQs[i].question_type == 'Multiple Selections':
                self.fields[field_name] = forms.ModelMultipleChoiceField(queryset=Option.objects.filter(pk__in=formQs[i].option_set.all()), widget=forms.CheckboxSelectMultiple)  
            


#resp (1)
#bg: created date (1)
#bg: created by user(1)
#question (nq)
    #option (no)
