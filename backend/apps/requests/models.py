"""
Service Request models for RoadAid Network.
Handles breakdown reports, helper matching, and service tracking.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.mixins import TimestampMixin


class ServiceRequest(TimestampMixin, models.Model):
    """
    Main service request model for breakdown/assistance requests.
    Tracks the full lifecycle from creation to completion.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SEARCHING = 'searching', _('Searching for Helper')
        MATCHED = 'matched', _('Helper Matched')
        ACCEPTED = 'accepted', _('Accepted by Helper')
        EN_ROUTE = 'en_route', _('Helper En Route')
        ARRIVED = 'arrived', _('Helper Arrived')
        IN_PROGRESS = 'in_progress', _('Service In Progress')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
        EXPIRED = 'expired', _('Expired')
    
    class UrgencyLevel(models.TextChoices):
        LOW = 'low', _('Low - Can Wait')
        MEDIUM = 'medium', _('Medium - Needs Help Soon')
        HIGH = 'high', _('High - Urgent')
        EMERGENCY = 'emergency', _('Emergency - Safety Risk')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Users involved
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='service_requests'
    )
    helper = models.ForeignKey(
        'helpers.Helper',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_requests'
    )
    
    # Request details
    vehicle_type = models.ForeignKey(
        'helpers.VehicleType',
        on_delete=models.PROTECT,
        related_name='requests'
    )
    service_types = models.ManyToManyField(
        'helpers.ServiceType',
        related_name='requests',
        blank=True
    )
    issue_description = models.TextField(help_text="Description of the problem")
    urgency = models.CharField(
        max_length=20,
        choices=UrgencyLevel.choices,
        default=UrgencyLevel.MEDIUM
    )
    
    # Location
    user_latitude = models.FloatField()
    user_longitude = models.FloatField()
    user_address = models.CharField(max_length=500, blank=True)
    
    helper_latitude = models.FloatField(null=True, blank=True)
    helper_longitude = models.FloatField(null=True, blank=True)
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    
    # Timing
    eta_minutes = models.PositiveIntegerField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    arrived_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Pricing
    estimated_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    final_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    is_barter = models.BooleanField(default=False)
    barter_terms = models.TextField(blank=True)
    
    # Media
    issue_images = models.JSONField(
        default=list,
        blank=True,
        help_text="List of image URLs showing the issue"
    )
    
    # Cancellation
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_requests'
    )
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('service request')
        verbose_name_plural = _('service requests')
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Request {self.id} - {self.status}"

    def can_be_accepted(self) -> bool:
        """Check if request can still be accepted by a helper."""
        return self.status in [self.Status.PENDING, self.Status.SEARCHING]

    def accept(self, helper):
        """
        Accept the request by a helper.
        
        Args:
            helper: Helper instance accepting the request
        """
        from django.utils import timezone
        from core.utils import calculate_distance, calculate_eta
        
        if not self.can_be_accepted():
            raise ValueError("Request cannot be accepted in its current status")
        
        self.helper = helper
        self.status = self.Status.ACCEPTED
        self.accepted_at = timezone.now()
        
        # Calculate ETA if helper location is available
        if helper.user.latitude and helper.user.longitude:
            self.helper_latitude = helper.user.latitude
            self.helper_longitude = helper.user.longitude
            distance = calculate_distance(
                self.user_latitude, self.user_longitude,
                helper.user.latitude, helper.user.longitude
            )
            self.eta_minutes = calculate_eta(distance)
        
        self.save()

    def update_helper_location(self, latitude: float, longitude: float):
        """
        Update helper's location during en-route status.
        
        Args:
            latitude: Current helper latitude
            longitude: Current helper longitude
        """
        from core.utils import calculate_distance, calculate_eta
        
        self.helper_latitude = latitude
        self.helper_longitude = longitude
        
        # Recalculate ETA
        distance = calculate_distance(
            self.user_latitude, self.user_longitude,
            latitude, longitude
        )
        self.eta_minutes = calculate_eta(distance)
        self.save(update_fields=['helper_latitude', 'helper_longitude', 'eta_minutes'])

    def mark_en_route(self):
        """Mark helper as en route to user."""
        from django.utils import timezone
        self.status = self.Status.EN_ROUTE
        self.save(update_fields=['status'])

    def mark_arrived(self):
        """Mark helper as arrived at user location."""
        from django.utils import timezone
        self.status = self.Status.ARRIVED
        self.arrived_at = timezone.now()
        self.save(update_fields=['status', 'arrived_at'])

    def start_service(self):
        """Mark service as in progress."""
        from django.utils import timezone
        self.status = self.Status.IN_PROGRESS
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def complete(self, final_price: float = None):
        """
        Mark request as completed.
        
        Args:
            final_price: Final service price
        """
        from django.utils import timezone
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if final_price is not None:
            self.final_price = final_price
        self.save()
        
        # Update helper stats
        if self.helper:
            self.helper.complete_job(float(self.final_price or 0))

    def cancel(self, cancelled_by_user, reason: str = ''):
        """
        Cancel the request.
        
        Args:
            cancelled_by_user: User who cancelled
            reason: Cancellation reason
        """
        from django.utils import timezone
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = cancelled_by_user
        self.cancellation_reason = reason
        self.save()


class RequestImage(models.Model):
    """
    Images attached to service requests.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='request_images/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']


class RequestStatusHistory(models.Model):
    """
    Track status changes for a request.
    """
    id = models.AutoField(primary_key=True)
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(max_length=20, choices=ServiceRequest.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Request status histories'
