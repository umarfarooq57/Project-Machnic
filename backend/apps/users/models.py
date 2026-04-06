"""
User models for RoadAid Network.
Custom user model with location support and helper profile extension.
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.mixins import TimestampMixin


class UserManager(BaseUserManager):
    """
    Custom user manager for User model with email as the username field.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimestampMixin):
    """
    Custom User model with email as the primary identifier.
    Supports location tracking and role-based access.
    """
    
    class Role(models.TextChoices):
        USER = 'user', _('User')
        HELPER = 'helper', _('Helper')
        ADMIN = 'admin', _('Admin')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    phone = models.CharField(_('phone number'), max_length=20, unique=True, null=True, blank=True)
    full_name = models.CharField(_('full name'), max_length=150)
    profile_image = models.ImageField(
        upload_to='profiles/', 
        null=True, 
        blank=True,
        help_text=_('User profile picture')
    )
    
    # Location fields (using simple float for SQLite compatibility, PostGIS Point for production)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Role and status
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Designates whether this user has verified their email/phone.')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Designates whether this user should be treated as active.'),
        db_index=True
    )
    is_staff = models.BooleanField(
        default=False,
        help_text=_('Designates whether the user can log into admin site.')
    )
    
    # FCM token for push notifications
    fcm_token = models.CharField(max_length=255, null=True, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else self.email

    @property
    def is_helper(self):
        """Check if user has a helper profile."""
        return hasattr(self, 'helper_profile') and self.helper_profile is not None

    def update_location(self, latitude: float, longitude: float):
        """
        Update user's current location.
        
        Args:
            latitude: New latitude value
            longitude: New longitude value
        """
        from django.utils import timezone
        self.latitude = latitude
        self.longitude = longitude
        self.last_location_update = timezone.now()
        self.save(update_fields=['latitude', 'longitude', 'last_location_update'])


class UserVerification(models.Model):
    """
    Stores verification codes for email/phone verification.
    """
    class VerificationType(models.TextChoices):
        EMAIL = 'email', _('Email Verification')
        PHONE = 'phone', _('Phone Verification')
        PASSWORD_RESET = 'password_reset', _('Password Reset')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    verification_type = models.CharField(max_length=20, choices=VerificationType.choices)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self) -> bool:
        """Check if the verification code is still valid."""
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()
