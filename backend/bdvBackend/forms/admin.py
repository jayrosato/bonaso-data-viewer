from django.contrib import admin

from .models import Question, Option

class OptionInline(admin.TabularInline):
    model=Option
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Information', {'fields': ['question_text']}),
        ('Date Information', {'fields': ['created_date'], 'classes':['collapse']}),
    ]
    inlines = [OptionInline]
    list_display=['question_text', 'created_date', 'options']
    list_filter = ['created_date']
    search_fields=['question_text']

admin.site.register(Question, QuestionAdmin)
