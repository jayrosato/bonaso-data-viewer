from django.urls import path

from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = "accounts"
urlpatterns = [
    path('settings', views.Settings.as_view(), name='settings'),
    path('profile/<int:pk>', views.Profile.as_view(), name='view-profile'),

    #api for mobile app
    path('mobile/verify', views.MobileLoginRequest.as_view(), name='mobile-verification'),
    path('api/health/', views.CheckAPI.as_view(), name='health-check'),
    path('api/token/', views.MyTokenObtainPairView.as_view(), name='mobile-login-token'),
    path('mobile/login/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]