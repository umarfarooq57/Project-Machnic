"""
WebSocket consumers for real-time request updates.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class RequestConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time request updates.
    Users and helpers can subscribe to request updates.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.request_id = self.scope['url_route']['kwargs'].get('request_id')
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        if self.request_id:
            # Subscribe to specific request updates
            self.room_group_name = f'request_{self.request_id}'
        else:
            # Subscribe to user's general request notifications
            self.room_group_name = f'user_{self.user.id}_requests'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to {self.room_group_name}'
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
            message_type = data.get('type')
            
            if message_type == 'location_update':
                # Helper sending location update
                await self.handle_location_update(data)
            elif message_type == 'ping':
                # Heartbeat
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def handle_location_update(self, data):
        """Handle helper location update."""
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is not None and longitude is not None:
            # Update request with new location
            await self.update_request_location(latitude, longitude)
            
            # Broadcast to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_broadcast',
                    'latitude': latitude,
                    'longitude': longitude,
                    'user_id': str(self.user.id)
                }
            )

    @database_sync_to_async
    def update_request_location(self, latitude, longitude):
        """Update request with helper's location."""
        from .models import ServiceRequest
        try:
            request = ServiceRequest.objects.get(id=self.request_id)
            if request.helper and request.helper.user == self.user:
                request.update_helper_location(latitude, longitude)
                return True
        except ServiceRequest.DoesNotExist:
            pass
        return False

    # Event handlers for group messages
    async def request_update(self, event):
        """Handle request update events."""
        await self.send(text_data=json.dumps({
            'type': 'request_update',
            'request_id': event.get('request_id'),
            'status': event.get('status'),
            'data': event.get('data', {})
        }))

    async def location_broadcast(self, event):
        """Handle location broadcast events."""
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'latitude': event.get('latitude'),
            'longitude': event.get('longitude'),
            'user_id': event.get('user_id')
        }))

    async def helper_matched(self, event):
        """Handle helper matched event."""
        await self.send(text_data=json.dumps({
            'type': 'helper_matched',
            'request_id': event.get('request_id'),
            'helper': event.get('helper'),
            'eta_minutes': event.get('eta_minutes')
        }))

    async def request_completed(self, event):
        """Handle request completed event."""
        await self.send(text_data=json.dumps({
            'type': 'request_completed',
            'request_id': event.get('request_id'),
            'final_price': event.get('final_price')
        }))


class HelperRequestsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for helpers to receive new request notifications.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user is a helper
        is_helper = await self.check_is_helper()
        if not is_helper:
            await self.close()
            return
        
        # Subscribe to helper's request channel
        self.room_group_name = f'helper_{self.user.id}_requests'
        
        # Also subscribe to nearby requests (based on location)
        # This would be more sophisticated in production
        self.nearby_group = 'nearby_requests'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.nearby_group,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        if hasattr(self, 'nearby_group'):
            await self.channel_layer.group_discard(
                self.nearby_group,
                self.channel_name
            )

    @database_sync_to_async
    def check_is_helper(self):
        """Check if user has a helper profile."""
        return hasattr(self.user, 'helper_profile') and self.user.helper_profile is not None

    async def receive(self, text_data):
        """Handle incoming messages."""
        try:
            data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except json.JSONDecodeError:
            pass

    async def new_request(self, event):
        """Handle new request notification."""
        await self.send(text_data=json.dumps({
            'type': 'new_request',
            'request': event.get('request'),
            'distance_km': event.get('distance_km'),
            'eta_minutes': event.get('eta_minutes')
        }))

    async def request_taken(self, event):
        """Handle notification that a request was taken by another helper."""
        await self.send(text_data=json.dumps({
            'type': 'request_taken',
            'request_id': event.get('request_id')
        }))
