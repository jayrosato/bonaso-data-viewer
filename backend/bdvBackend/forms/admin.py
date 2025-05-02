from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms

from .models import Organization, Respondent, Form, FormQuestion, Question, Option, UserProfile

class OrganizationAdmin(admin.ModelAdmin):
    fieldsets = [('Basic Information', {'fields': ['organization_name']})]

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name='user'
    can_delete = False
    verbose_name_plural = 'Profile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

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


'''
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Information', {'fields': ['question_text']}),
        ('Question Information', {'fields': ['question_type'], 'classes':['collapse']}),
    ]
    inlines = [OptionInline]
    list_display=['question_text', 'created_date', 'options']
    list_filter = ['created_date']
    search_fields=['question_text']
'''

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Respondent, RespondentAdmin)
admin.site.register(Form, FormAdmin)
admin.site.register(Question, QuestionAdmin)
