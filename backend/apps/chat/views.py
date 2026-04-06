"""
Chat views.
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from apps.users.permissions import IsRequestParticipant
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer, ChatMessageCreateSerializer


@extend_schema(tags=['Chat'])
class ChatRoomView(generics.RetrieveAPIView):
    """
    Get chat room for a specific request.
    Creates the room if it doesn't exist.
    """
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        from apps.requests.models import ServiceRequest
        request_id = self.kwargs['request_id']
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Check if user is a participant
        is_participant = (
            service_request.user == self.request.user or
            (service_request.helper and service_request.helper.user == self.request.user)
        )
        if not is_participant:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not a participant in this request.")
        
        # Get or create chat room
        room, created = ChatRoom.objects.get_or_create(request=service_request)
        return room


@extend_schema(tags=['Chat'])
class ChatMessagesListView(generics.ListAPIView):
    """
    List messages in a chat room.
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        room = get_object_or_404(ChatRoom, id=room_id)
        
        # Check participation
        request = room.request
        is_participant = (
            request.user == self.request.user or
            (request.helper and request.helper.user == self.request.user)
        )
        if not is_participant:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not a participant in this chat.")
        
        return ChatMessage.objects.filter(room=room).select_related('sender')


@extend_schema(tags=['Chat'])
class SendMessageView(generics.CreateAPIView):
    """
    Send a message in a chat room.
    """
    serializer_class = ChatMessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        room_id = self.kwargs['room_id']
        room = get_object_or_404(ChatRoom, id=room_id)
        
        # Check participation
        service_request = room.request
        is_participant = (
            service_request.user == request.user or
            (service_request.helper and service_request.helper.user == request.user)
        )
        if not is_participant:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not a participant in this chat.")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = ChatMessage.objects.create(
            room=room,
            sender=request.user,
            **serializer.validated_data
        )
        
        # Broadcast via WebSocket
        self._broadcast_message(room, message)
        
        return Response(
            ChatMessageSerializer(message, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def _broadcast_message(self, room, message):
        """Broadcast new message via WebSocket."""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{room.id}',
            {
                'type': 'chat_message',
                'message': ChatMessageSerializer(message).data
            }
        )


@extend_schema(tags=['Chat'])
class MarkMessagesReadView(APIView):
    """
    Mark all messages in a room as read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        
        # Check participation
        service_request = room.request
        is_participant = (
            service_request.user == request.user or
            (service_request.helper and service_request.helper.user == request.user)
        )
        if not is_participant:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not a participant in this chat.")
        
        # Mark messages from other user as read
        from django.utils import timezone
        updated = ChatMessage.objects.filter(
            room=room,
            is_read=False
        ).exclude(sender=request.user).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({'marked_read': updated})
