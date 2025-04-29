from django.urls import path

from . import views

app_name = "forms"
urlpatterns = [
    path('', views.ViewFormsIndex.as_view(), name='view-forms-index'),
    path('<int:pk>/view', views.ViewFormDetail.as_view(), name='view-form-detail'),
    path('create', views.CreateForm.as_view(), name='create-form'),
    path('<int:pk>/update', views.UpdateForm.as_view(), name='update-form'),
    path('<int:pk>/delete', views.DeleteForm.as_view(), name='delete-form'),
    path('<int:pk>/template', views.FormTemplate.as_view(), name='form-template'),
    


    path('data', views.Data.as_view(), name='data'),
    path('data/get', views.GetData.as_view(), name='data-get'),

    path('questions/create', views.CreateQuestion.as_view(), name='create-question'),
    path('questions/<int:pk>/update', views.UpdateQuestion.as_view(), name='update-question'),
    path('questions/<int:pk>/delete', views.DeleteQuestion.as_view(), name='delete-question'),

    path('organizations', views.ViewOrgsIndex.as_view(), name='view-orgs-index'),
    path('organizations/<int:pk>', views.ViewOrgDetail.as_view(), name='view-org-detail'),
    path('organizations/create', views.CreateOrg.as_view(), name='create-org'),
    path('organizations/<int:pk>/update', views.UpdateOrg.as_view(), name='update-org'),
    path('organizations/<int:pk>/delete', views.DeleteOrg.as_view(), name='delete-org'),


    #allows users to view, create, and edit respondents (demographic data collected about clients)
    path('respondents', views.ViewRespondentsIndex.as_view(), name='view-respondents-index'),
    path('respondents/create', views.CreateRespondent.as_view(), name='create-respondent'),
    path('respondents/<int:pk>', views.ViewRespondentDetail.as_view(), name='view-respondent-detail'),
    path('respondents/<int:pk>/update', views.UpdateRespondent.as_view(), name='update-respondent'),
    path('respondents/<int:pk>/delete', views.DeleteRespondent.as_view(), name='delete-respondent'),

    #allows users to view, create, andedit responses given by respondents
    path('response', views.ViewResponseIndex.as_view(), name='view-responses-index'),
    path('response/<int:pk>', views.ViewResponseDetail.as_view(), name='view-response-detail'),
    path('response/<int:pk>/create', views.NewResponse.as_view(), name='create-response'),
    path('response/<int:pk>/update', views.UpdateResponse.as_view(), name='update-response'),
    path('response/<int:pk>/delete', views.DeleteResponse.as_view(), name='delete-response'),
]