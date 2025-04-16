from django import forms
from django.forms import ModelForm

from .models import Respondent, Question

class SelectRespondentForm(forms.Form):
    respondent = forms.ModelChoiceField(queryset=Respondent.objects.all(), label='Respondent')

class RespondentForm(ModelForm):
    class Meta:
        model=Respondent
        fields = [
            'id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship', 'ward', 'village', 
            'district', 'email', 'contact_no'
            ] 

