from django.urls import path

from . import views

app_name = "forms"
urlpatterns = [
    path('', views.ViewFormsIndex.as_view(), name='index'),
    path('forms', views.ViewFormsIndex.as_view(), name='view-forms-index'),
    path('<int:pk>', views.ViewFormDetail.as_view(), name='view-form-detail'),
    #allows users to create/edit respondents (demographic data collected about clients)
    path('respondents', views.ViewRespondentsIndex.as_view(), name='view-respondents-index'),
    path('respondents/create', views.CreateRespondent.as_view(), name='create-respondent'),
    path('respondents/<int:pk>', views.ViewRespondentDetail.as_view(), name='view-respondent-detail'),
    path('respondents/<int:pk>/update', views.UpdateRespondent.as_view(), name='update-respondent'),
    path('respondents/<int:pk>/delete', views.DeleteRespondent.as_view(), name='delete-respondent'),

    #allows users to collect information about specific indicators related to respondents
    #path('<int:pk>/new', views.new_response, name='new-response'),
    #path('<int:pk>/responses/', views.ResponsesView.as_view(), name='responses'),
    #path('<int:question_id>/respond/', views.ResponsesView.as_view(), name='respond'),

    #allows users to create/edit responses given by respondents
    path('response/<int:pk>', views.ViewResponseDetail.as_view(), name='view-response-detail'),
    path('response/<int:pk>/create', views.NewResponse.as_view(), name='create-response'),
    path('response/<int:pk>/update', views.UpdateResponse.as_view(), name='update-response'),
    path('response/<int:pk>/delete', views.DeleteResponse.as_view(), name='delete-response'),
]