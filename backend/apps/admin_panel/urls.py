"""
Admin Panel URL configuration.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DashboardStatsView.as_view(), name='admin-dashboard'),
    path('revenue-report/', views.RevenueReportView.as_view(), name='admin-revenue-report'),

    # User management
    path('users/', views.AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<uuid:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),

    # Helper verification
    path('helpers/', views.AdminHelperListView.as_view(), name='admin-helper-list'),
    path('helpers/<uuid:pk>/verify/', views.AdminHelperVerifyView.as_view(), name='admin-helper-verify'),

    # Promo codes
    path('promo-codes/', views.PromoCodeListCreateView.as_view(), name='admin-promo-list'),
    path('promo-codes/<uuid:pk>/', views.PromoCodeDetailView.as_view(), name='admin-promo-detail'),
    path('promo-codes/apply/', views.ApplyPromoCodeView.as_view(), name='promo-apply'),

    # Disputes
    path('disputes/', views.DisputeListView.as_view(), name='admin-dispute-list'),
    path('disputes/create/', views.DisputeCreateView.as_view(), name='dispute-create'),
    path('disputes/<uuid:pk>/resolve/', views.DisputeResolveView.as_view(), name='admin-dispute-resolve'),

    # Platform config
    path('config/', views.PlatformConfigListView.as_view(), name='admin-config-list'),
    path('config/<str:pk>/', views.PlatformConfigDetailView.as_view(), name='admin-config-detail'),

    # Emergency contacts (user-facing, grouped under admin for routing)
    path('emergency-contacts/', views.EmergencyContactListCreateView.as_view(), name='emergency-contact-list'),
    path('emergency-contacts/<uuid:pk>/', views.EmergencyContactDetailView.as_view(), name='emergency-contact-detail'),
]
