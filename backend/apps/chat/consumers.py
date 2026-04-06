"""
WebSocket consumers for real-time chat.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat within a request.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        # Verify user is a participant in this chat room
        is_participant = await self.check_participant()
        if not is_participant:
            await self.close()
            return
        
        self.room_group_name = f'chat_{self.room_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Send recent messages on connect
        recent_messages = await self.get_recent_messages()
        await self.send(text_data=json.dumps({
            'type': 'history',
            'messages': recent_messages
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read':
                await self.handle_read(data)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def handle_message(self, data):
        """Handle new message."""
        content = data.get('content', '').strip()
        msg_type = data.get('message_type', 'text')
        
        if not content and msg_type == 'text':
            return
        
        # Save message to database
        message_data = await self.save_message(content, msg_type, data)
        
        if message_data:
            # Broadcast to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )

    async def handle_typing(self, data):
        """Handle typing indicator."""
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'user_name': self.user.full_name,
                'is_typing': is_typing
            }
        )

    async def handle_read(self, data):
        """Handle message read receipts."""
        message_id = data.get('message_id')
        if message_id:
            await self.mark_message_read(message_id)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_read',
                    'message_id': message_id,
                    'reader_id': str(self.user.id)
                }
            )

    @database_sync_to_async
    def check_participant(self):
        """Check if user is a participant in the chat room."""
        from .models import ChatRoom
        try:
            room = ChatRoom.objects.select_related('request__user', 'request__helper__user').get(id=self.room_id)
            # User is either the requester or the helper
            is_requester = room.request.user == self.user
            is_helper = (room.request.helper and room.request.helper.user == self.user)
            return is_requester or is_helper
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def get_recent_messages(self, limit=50):
        """Get recent messages from the chat room."""
        from .models import ChatRoom, ChatMessage
        from .serializers import ChatMessageSerializer
        
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            messages = room.messages.select_related('sender').order_by('-sent_at')[:limit]
            # Return in chronological order
            messages = list(reversed(messages))
            return ChatMessageSerializer(messages, many=True).data
        except ChatRoom.DoesNotExist:
            return []

    @database_sync_to_async
    def save_message(self, content, msg_type, data):
        """Save message to database."""
        from .models import ChatRoom, ChatMessage
        from .serializers import ChatMessageSerializer
        
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            
            message = ChatMessage.objects.create(
                room=room,
                sender=self.user,
                message_type=msg_type,
                content=content,
                latitude=data.get('latitude'),
                longitude=data.get('longitude')
            )
            
            return ChatMessageSerializer(message).data
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def mark_message_read(self, message_id):
        """Mark a message as read."""
        from .models import ChatMessage
        try:
            message = ChatMessage.objects.get(id=message_id)
            if message.sender != self.user:
                message.mark_as_read()
        except ChatMessage.DoesNotExist:
            pass

    # Event handlers
    async def chat_message(self, event):
        """Handle chat message event."""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))

    async def typing_indicator(self, event):
        """Handle typing indicator event."""
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing']
            }))

    async def message_read(self, event):
        """Handle message read event."""
        await self.send(text_data=json.dumps({
            'type': 'read',
            'message_id': event['message_id'],
            'reader_id': event['reader_id']
        }))
