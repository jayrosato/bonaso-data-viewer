from django.urls import path

from . import views

app_name = "forms"
urlpatterns = [
    path('', views.ViewFormsIndex.as_view(), name='view-forms-index'),
    path('past', views.ViewPastForms.as_view(), name='view-past-forms'),
    path('<int:pk>/view', views.ViewFormDetail.as_view(), name='view-form-detail'),
    path('create', views.CreateUpdateForm.as_view(), name='create-form'),
    path('<int:pk>/update', views.CreateUpdateForm.as_view(), name='update-form'),
    path('<int:pk>/duplicate', views.DuplicateForm.as_view(), name='duplicate-form'),
    path('<int:pk>/delete', views.DeleteForm.as_view(), name='delete-form'),
    path('<int:pk>/template', views.FormTemplate.as_view(), name='form-template'),
    
    path('dashboard', views.Dashboard.as_view(), name='dashboard'),
    path('data/get', views.GetData.as_view(), name='data-get'),

    path('questions', views.ViewQuestions.as_view(), name='view-questions'),
    path('questions/create', views.CreateQuestion.as_view(), name='create-question'),
    path('questions/<int:pk>/update', views.UpdateQuestion.as_view(), name='update-question'),
    path('questions/<int:pk>/delete', views.DeleteQuestion.as_view(), name='delete-question'),

    #allows users to view, create, and edit respondents (demographic data collected about clients)
    path('respondents', views.ViewRespondentsIndex.as_view(), name='view-respondents-index'),
    path('respondents/create', views.CreateRespondent.as_view(), name='create-respondent'),
    path('respondents/<int:pk>', views.ViewRespondentDetail.as_view(), name='view-respondent-detail'),
    path('respondents/<int:pk>/update', views.UpdateRespondent.as_view(), name='update-respondent'),
    path('respondents/<int:pk>/delete', views.DeleteRespondent.as_view(), name='delete-respondent'),

    #allows users to view, create, andedit responses given by respondents
    path('response', views.ViewResponseIndex.as_view(), name='view-responses-index'),
    path('response/<int:pk>', views.ViewResponseDetail.as_view(), name='view-response-detail'),
    path('response/<int:pk>/create', views.RecordResponse.as_view(), name='create-response'),
    path('response/<int:pk>/update/<int:rid>', views.RecordResponse.as_view(), name='update-response'),
    path('response/<int:pk>/delete', views.DeleteResponse.as_view(), name='delete-response'),

    #related to getting specific queries
    path('data/query/questions/<int:pk>/meta', views.GetQuestionInfo.as_view()),
    path('data/query/questions', views.GetQuestions.as_view()),
    path('data/query/questions/<int:pk>', views.GetQuestionData.as_view(), name='data-get-q'),
    path('data/query/questions/responses', views.GetQuestionResponses.as_view()),
    path('data/query/forms/<int:pk>', views.GetFormInfo.as_view()),

    #testing mobile development
    path('mobile/getforms/<int:pk>', views.GetForms.as_view()),
    path('mobile/sync/responses', views.SyncMobileResponses.as_view()),
]