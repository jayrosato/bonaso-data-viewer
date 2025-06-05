from django.contrib import admin
from django import forms

from forms.models import Respondent, Form, FormQuestion, Question, Option

class RespondentAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Information', {'fields': ['id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship']}),
        ('Geographic Information', {'fields': ['ward', 'village', 'district']}),
        ('Contact Information', {'fields':['email', 'contact_no']})
    ]

class OptionInline(admin.TabularInline):
    model=Option
    extra = 2

class FormQuestionInline(admin.TabularInline):
    model=FormQuestion
    extra = 3

class FormAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Information', {'fields': ['form_name', 'organization']}),
        ('Start/End', {'fields': ['start_date', 'end_date']})
    ]
    inlines = [FormQuestionInline]

class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    inlines = [OptionInline]
    class Media:
        js = (
            'admin/js/jquery.init.js',
            'forms/question_admin.js',
        )


admin.site.register(Respondent, RespondentAdmin)
admin.site.register(Form, FormAdmin)
admin.site.register(Question, QuestionAdmin)
