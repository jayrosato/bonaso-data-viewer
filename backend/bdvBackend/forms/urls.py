from django.urls import path

from . import views

app_name = "forms"
urlpatterns = [
    path("", views.index, name="index"),
    path('<int:question_id>/', views.detail, name='detail'),
    path('<int:question_id>/responses/', views.responses, name='responses'),
    path('<int:question_id>/respond/', views.respond, name='respond'),
]