from django.urls import path

from . import views

app_name = "forms"
urlpatterns = [
    path('', views.ViewFormsIndex.as_view(), name='view-forms-index'),
    path('<int:pk>/view', views.ViewFormDetail.as_view(), name='view-form-detail'),
    path('new', views.CreateForm.as_view(), name='create-form'),
    path('<int:pk>/update', views.UpdateForm.as_view(), name='update-form'),
    path('<int:pk>/delete', views.DeleteForm.as_view(), name='delete-form'),



    path('<int:form_id>/formquestions/create', views.CreateFormQuestion.as_view(), name='create-form-question'),
    path('<int:form_id>/formquestions/<int:pk>/update', views.UpdateFormQuestion.as_view(), name='update-form-question'),
    path('formquestions/<int:pk>/remove', views.RemoveFormQuestion.as_view(), name='remove-form-question'),

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
    path('response/<int:pk>', views.ViewResponseDetail.as_view(), name='view-response-detail'),
    path('response/<int:pk>/create', views.NewResponse.as_view(), name='create-response'),
    path('response/<int:pk>/update', views.UpdateResponse.as_view(), name='update-response'),
    path('response/<int:pk>/delete', views.DeleteResponse.as_view(), name='delete-response'),
]