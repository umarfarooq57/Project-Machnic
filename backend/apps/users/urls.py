"""
URL configuration for users app.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    UserProfileView,
    UserLocationUpdateView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    FCMTokenUpdateView,
    DeleteAccountView,
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Password management
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Profile management
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/location/', UserLocationUpdateView.as_view(), name='location-update'),
    path('profile/fcm-token/', FCMTokenUpdateView.as_view(), name='fcm-token-update'),
    path('profile/delete/', DeleteAccountView.as_view(), name='delete-account'),
]
