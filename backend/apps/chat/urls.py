"""
URL configuration for chat app.
"""
from django.urls import path
from .views import (
    ChatRoomView,
    ChatMessagesListView,
    SendMessageView,
    MarkMessagesReadView,
)

app_name = 'chat'

urlpatterns = [
    path('request/<uuid:request_id>/', ChatRoomView.as_view(), name='room-by-request'),
    path('<uuid:room_id>/messages/', ChatMessagesListView.as_view(), name='messages'),
    path('<uuid:room_id>/send/', SendMessageView.as_view(), name='send'),
    path('<uuid:room_id>/read/', MarkMessagesReadView.as_view(), name='mark-read'),
]
