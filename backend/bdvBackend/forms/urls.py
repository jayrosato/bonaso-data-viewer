from django.urls import path

from . import views

app_name = "forms"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('forms', views.IndexView.as_view(), name="forms"),

    #allows users to create/edit respondents (demographic data collected about clients)
    path('respondents', views.ViewRespondents.as_view(), name='respondents'),
    path('respondents/create', views.CreateRespondent.as_view(), name='create-respondent'),
    path('respondents/<int:pk>/update', views.UpdateRespondent.as_view(), name='update-respondent'),
    path('respondents/<int:pk>/delete', views.DeleteRespondent.as_view(), name='delete-respondent'),

    #allows users to collect information about specific indicators related to respondents
    path('<int:pk>/', views.FormView.as_view(), name='form-detail'),
    path('<int:pk>/new', views.new_response, name='new-response'),
    path('<int:pk>/responses/', views.ResponsesView.as_view(), name='responses'),
    path('<int:question_id>/respond/', views.ResponsesView.as_view(), name='respond'),
]