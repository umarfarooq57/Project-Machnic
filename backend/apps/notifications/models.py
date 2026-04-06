"""
Notification models for RoadAid Network.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """
    In-app notification model.
    """
    
    class NotificationType(models.TextChoices):
        NEW_REQUEST = 'new_request', _('New Request')
        REQUEST_ACCEPTED = 'request_accepted', _('Request Accepted')
        HELPER_EN_ROUTE = 'helper_en_route', _('Helper En Route')
        HELPER_ARRIVED = 'helper_arrived', _('Helper Arrived')
        SERVICE_COMPLETED = 'service_completed', _('Service Completed')
        REQUEST_CANCELLED = 'request_cancelled', _('Request Cancelled')
        NEW_MESSAGE = 'new_message', _('New Message')
        PAYMENT_RECEIVED = 'payment_received', _('Payment Received')
        RATING_RECEIVED = 'rating_received', _('Rating Received')
        SYSTEM = 'system', _('System Notification')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    
    # Additional data for deep linking
    data = models.JSONField(default=dict, blank=True)
    
    # Reference to related request (if applicable)
    request = models.ForeignKey(
        'requests.ServiceRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class Rating(models.Model):
    """
    Rating model for service reviews.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(
        'requests.ServiceRequest',
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings_given'
    )
    rated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings_received'
    )
    score = models.PositiveSmallIntegerField(
        help_text="Rating from 1-5"
    )
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        # One rating per user per request
        unique_together = ['request', 'rater']

    def __str__(self):
        return f"Rating {self.score}/5 by {self.rater} for {self.rated_user}"

    def save(self, *args, **kwargs):
        # Validate score
        if not 1 <= self.score <= 5:
            raise ValueError("Score must be between 1 and 5")
        super().save(*args, **kwargs)
        
        # Update helper's average rating if rated user is a helper
        if hasattr(self.rated_user, 'helper_profile'):
            self.rated_user.helper_profile.update_rating(self.score)
