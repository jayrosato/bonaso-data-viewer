from django.urls import path

from . import views

app_name = "forms"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/responses/', views.ResponsesView.as_view(), name='responses'),
    path('<int:question_id>/respond/', views.respond, name='respond'),
]