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
    path('messages', views.ViewMessagesIndex.as_view(), name='view-messages-index'),
    path('messages/<int:pk>', views.ViewMessageDetail.as_view(), name='view-message-detail'),
    path('messages/compose', views.CreateMessage.as_view(), name='compose-message'),
    path('messages/<int:pk>/edit', views.UpdateMessage.as_view(), name='update-message'),
    path('messages/<int:pk>/reply', views.CreateReply.as_view(), name='reply'),
    path('messages/<int:pk>/complete', views.CompleteMessage.as_view(), name='complete-message'),
    path('messages/<int:pk>/delete', views.DeleteMessage.as_view(), name='delete-message'),

    #api for mobile app
    path('mobile/verify', views.MobileLoginRequest.as_view(), name='mobile-verification'),
    path('api/health/', views.CheckAPI.as_view(), name='health-check'),
    path('api/token/', views.MyTokenObtainPairView.as_view(), name='mobile-login-token'),
    path('mobile/login/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]