"""
URL configuration for notifications app.
"""
from django.urls import path
from .views import (
    NotificationListView,
    UnreadNotificationsView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
    CreateRatingView,
    RequestRatingsView,
    UserRatingsView,
)

app_name = 'notifications'

urlpatterns = [
    # Notifications
    path('', NotificationListView.as_view(), name='list'),
    path('unread/', UnreadNotificationsView.as_view(), name='unread'),
    path('<uuid:pk>/read/', MarkNotificationReadView.as_view(), name='mark-read'),
    path('read-all/', MarkAllNotificationsReadView.as_view(), name='mark-all-read'),
    
    # Ratings
    path('ratings/request/<uuid:request_id>/', CreateRatingView.as_view(), name='create-rating'),
    path('ratings/request/<uuid:request_id>/list/', RequestRatingsView.as_view(), name='request-ratings'),
    path('ratings/my/', UserRatingsView.as_view(), name='my-ratings'),
]
