"""
Chat serializers.
"""
from rest_framework import serializers
from apps.users.serializers import UserPublicSerializer
from .models import ChatRoom, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for chat messages.
    """
    sender = UserPublicSerializer(read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    is_own_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender', 'sender_name', 'message_type', 'content',
            'image', 'latitude', 'longitude',
            'is_read', 'read_at', 'sent_at', 'is_own_message'
        ]
        read_only_fields = ['id', 'sender', 'sent_at', 'is_read', 'read_at']

    def get_is_own_message(self, obj):
        request = self.context.get('request')
        if request and obj.sender:
            return obj.sender == request.user
        return False


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating chat messages.
    """
    class Meta:
        model = ChatMessage
        fields = ['message_type', 'content', 'image', 'latitude', 'longitude']

    def validate(self, attrs):
        message_type = attrs.get('message_type', ChatMessage.MessageType.TEXT)
        
        if message_type == ChatMessage.MessageType.TEXT and not attrs.get('content'):
            raise serializers.ValidationError({'content': 'Content is required for text messages.'})
        
        if message_type == ChatMessage.MessageType.IMAGE and not attrs.get('image'):
            raise serializers.ValidationError({'image': 'Image is required for image messages.'})
        
        if message_type == ChatMessage.MessageType.LOCATION:
            if not attrs.get('latitude') or not attrs.get('longitude'):
                raise serializers.ValidationError('Latitude and longitude are required for location messages.')
        
        return attrs


class ChatRoomSerializer(serializers.ModelSerializer):
    """
    Serializer for chat rooms.
    """
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    request_id = serializers.UUIDField(source='request.id', read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'request_id', 'is_active', 'last_message', 'unread_count', 'created_at']

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return ChatMessageSerializer(last_msg, context=self.context).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
