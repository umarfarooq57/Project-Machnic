"""
Chat models for RoadAid Network.
Real-time messaging between users and helpers within service requests.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.mixins import TimestampMixin


class ChatRoom(TimestampMixin, models.Model):
    """
    Chat room for a service request.
    Each request has one chat room for user-helper communication.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.OneToOneField(
        'requests.ServiceRequest',
        on_delete=models.CASCADE,
        related_name='chat_room'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat for Request {self.request_id}"


class ChatMessage(models.Model):
    """
    Individual chat message within a chat room.
    """
    
    class MessageType(models.TextChoices):
        TEXT = 'text', _('Text')
        IMAGE = 'image', _('Image')
        LOCATION = 'location', _('Location')
        SYSTEM = 'system', _('System Message')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        null=True,  # Null for system messages
        blank=True
    )
    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.TEXT
    )
    content = models.TextField()
    
    # For image messages
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    
    # For location messages
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Read status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        sender_name = self.sender.full_name if self.sender else 'System'
        return f"{sender_name}: {self.content[:50]}"

    def mark_as_read(self):
        """Mark the message as read."""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
