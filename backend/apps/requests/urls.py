"""
URL configuration for requests app.
"""
from django.urls import path
from .views import (
    CreateRequestView,
    RequestDetailView,
    UserRequestsListView,
    HelperRequestsListView,
    AvailableRequestsView,
    AcceptRequestView,
    UpdateRequestStatusView,
    CancelRequestView,
    UpdateHelperLocationView,
    RequestStatusHistoryView,
)
from .sos_views import TriggerSOSView as SosView

app_name = 'requests'

urlpatterns = [
    # Request CRUD
    path('', CreateRequestView.as_view(), name='request-create'),
    path('<uuid:pk>/', RequestDetailView.as_view(), name='detail'),
    
    # Request lists
    path('my/', UserRequestsListView.as_view(), name='user-list'),
    path('helper/', HelperRequestsListView.as_view(), name='helper-list'),
    path('available/', AvailableRequestsView.as_view(), name='available'),
    
    # Request actions
    path('<uuid:pk>/accept/', AcceptRequestView.as_view(), name='accept'),
    path('<uuid:pk>/status/', UpdateRequestStatusView.as_view(), name='update-status'),
    path('<uuid:pk>/cancel/', CancelRequestView.as_view(), name='cancel'),
    path('<uuid:pk>/location/', UpdateHelperLocationView.as_view(), name='update-location'),
    path('<uuid:pk>/history/', RequestStatusHistoryView.as_view(), name='status-history'),

    # SOS
    path('sos/', SosView.as_view(), name='sos'),
]
