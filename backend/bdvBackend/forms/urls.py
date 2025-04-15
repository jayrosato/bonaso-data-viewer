from django.urls import path

from . import views

app_name = "forms"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path('<int:pk>/', views.FormView.as_view(), name='form'),
    path('<int:pk>/responses/', views.ResponsesView.as_view(), name='responses'),
    path('<int:question_id>/respond/', views.respond, name='respond'),
]