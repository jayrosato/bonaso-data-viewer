from django.urls import path

from . import views

app_name = "dataviewer"
urlpatterns = [
    path('create/chart', views.CreateChart.as_view(), name='create-chart'),
]