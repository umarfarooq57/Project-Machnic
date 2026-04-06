"""
URL configuration for helpers app.
"""
from django.urls import path
from .views import (
    HelperRegistrationView,
    HelperProfileView,
    HelperDetailView,
    HelperAvailabilityView,
    NearbyHelpersView,
    HelperScheduleListView,
    HelperScheduleDetailView,
    VehicleTypeListView,
    ServiceTypeListView,
    ServiceLocationListView,
)

app_name = 'helpers'

urlpatterns = [
    # Helper registration and profile
    path('register/', HelperRegistrationView.as_view(), name='register'),
    path('profile/', HelperProfileView.as_view(), name='profile'),
    path('<uuid:pk>/', HelperDetailView.as_view(), name='detail'),
    
    # Availability
    path('availability/', HelperAvailabilityView.as_view(), name='availability'),
    
    # Nearby helpers search
    path('nearby/', NearbyHelpersView.as_view(), name='nearby'),
    
    # Schedules
    path('schedules/', HelperScheduleListView.as_view(), name='schedule-list'),
    path('schedules/<int:pk>/', HelperScheduleDetailView.as_view(), name='schedule-detail'),
    
    # Configuration - vehicle, service types, and locations
    path('vehicle-types/', VehicleTypeListView.as_view(), name='vehicle-types'),
    path('service-types/', ServiceTypeListView.as_view(), name='service-types'),
    path('locations/', ServiceLocationListView.as_view(), name='locations'),
]

