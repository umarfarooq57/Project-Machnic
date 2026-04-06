"""
Helper models for RoadAid Network.
Manages mechanic/helper profiles, availability, and specializations.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.mixins import TimestampMixin


class ServiceLocation(models.Model):
    """
    Service locations/cities where helpers can operate.
    Supports hierarchical locations (city -> region -> country).
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    name_urdu = models.CharField(max_length=100, blank=True, help_text="Name in Urdu")
    code = models.CharField(max_length=20, unique=True, help_text="Unique code like 'LHR', 'PKN'")
    latitude = models.FloatField(null=True, blank=True, help_text="Center latitude")
    longitude = models.FloatField(null=True, blank=True, help_text="Center longitude")
    radius_km = models.FloatField(default=50, help_text="Coverage radius in km")
    is_nationwide = models.BooleanField(default=False, help_text="True for 'All Pakistan' option")
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0, help_text="Order in dropdown list")

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = _('service location')
        verbose_name_plural = _('service locations')

    def __str__(self):
        return self.name


class VehicleType(models.Model):
    """
    Types of vehicles that can be serviced.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, help_text="Icon name or emoji")
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Base service price for this vehicle type"
    )
    price_multiplier = models.FloatField(
        default=1.0,
        help_text="Price multiplier for this vehicle type"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ServiceType(models.Model):
    """
    Types of services that helpers can provide.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    estimated_duration_minutes = models.IntegerField(
        default=30,
        help_text="Estimated duration to complete this service"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Helper(TimestampMixin, models.Model):
    """
    Helper/Mechanic profile attached to a User.
    Contains professional information and availability status.
    """
    
    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', _('Pending Review')
        VERIFIED = 'verified', _('Verified')
        REJECTED = 'rejected', _('Rejected')
        SUSPENDED = 'suspended', _('Suspended')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='helper_profile'
    )
    
    # Professional info
    license_number = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Professional license or ID number"
    )
    bio = models.TextField(
        blank=True,
        help_text="Short bio or description of services"
    )
    years_experience = models.PositiveIntegerField(default=0)
    
    # Specializations
    vehicle_types = models.ManyToManyField(
        VehicleType,
        related_name='helpers',
        blank=True,
        help_text="Vehicle types this helper can service"
    )
    service_types = models.ManyToManyField(
        ServiceType,
        related_name='helpers',
        blank=True,
        help_text="Services this helper can provide"
    )
    
    # Availability
    is_available = models.BooleanField(
        default=False,
        help_text="Whether helper is currently available for jobs",
        db_index=True
    )
    is_online = models.BooleanField(default=False)
    last_online = models.DateTimeField(null=True, blank=True)
    
    # Service area (radius from current location)
    service_radius_km = models.FloatField(
        default=10.0,
        help_text="Maximum distance (km) helper will travel"
    )
    
    # Ratings and stats
    rating_avg = models.FloatField(default=0.0, db_index=True)
    rating_count = models.PositiveIntegerField(default=0)
    total_jobs = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Verification
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    id_document = models.ImageField(
        upload_to='helper_documents/id/',
        null=True,
        blank=True,
        help_text="Government-issued ID for verification"
    )
    license_document = models.ImageField(
        upload_to='helper_documents/license/',
        null=True,
        blank=True,
        help_text="Professional license/certification document"
    )

    class Meta:
        ordering = ['-rating_avg', '-total_jobs']
        verbose_name = _('helper')
        verbose_name_plural = _('helpers')

    def __str__(self):
        return f"{self.user.full_name} - Helper"

    @property
    def is_verified(self):
        return self.verification_status == self.VerificationStatus.VERIFIED

    def update_rating(self, new_rating: int):
        """
        Update the average rating with a new rating.
        Uses incremental average calculation.
        
        Args:
            new_rating: Rating value (1-5)
        """
        total_ratings = self.rating_count * self.rating_avg
        self.rating_count += 1
        self.rating_avg = round((total_ratings + new_rating) / self.rating_count, 2)
        self.save(update_fields=['rating_avg', 'rating_count'])

    def complete_job(self, earnings: float = 0):
        """
        Record a completed job.
        
        Args:
            earnings: Amount earned from the job
        """
        from decimal import Decimal
        self.total_jobs += 1
        self.total_earnings += Decimal(str(earnings))
        self.save(update_fields=['total_jobs', 'total_earnings'])

    def toggle_availability(self, is_available: bool = None):
        """
        Toggle or set availability status.
        
        Args:
            is_available: If provided, sets to this value. Otherwise toggles.
        """
        from django.utils import timezone
        if is_available is not None:
            self.is_available = is_available
        else:
            self.is_available = not self.is_available
        
        self.is_online = self.is_available
        if self.is_online:
            self.last_online = timezone.now()
        self.save(update_fields=['is_available', 'is_online', 'last_online'])


class HelperSchedule(models.Model):
    """
    Weekly availability schedule for helpers.
    """
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    id = models.AutoField(primary_key=True)
    helper = models.ForeignKey(
        Helper,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['helper', 'day_of_week', 'start_time']

    def __str__(self):
        return f"{self.helper.user.full_name} - {self.get_day_of_week_display()}"
