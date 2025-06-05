from django import forms
from django.forms import ModelForm
from django.forms import inlineformset_factory
from django.db.models import Q
from .models import Target

class DateInput(forms.DateInput):
    input_type = 'date'

class TargetForm(forms.ModelForm):
    class Meta: 
        model=Target
        fields = [
            'question', 'organization', 'target_amount', 'percentage_of_question', 'as_percentage',
            'target_start', 'target_end', 'match_option',
            ]
        widgets = {
            'target_start': DateInput(), 'target_end':DateInput()
        }

