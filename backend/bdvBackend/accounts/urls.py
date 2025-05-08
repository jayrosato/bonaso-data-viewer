from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path('settings', views.Settings.as_view(), name='settings'),
    path('profile/<int:pk>', views.Profile.as_view(), name='view-profile'),
]