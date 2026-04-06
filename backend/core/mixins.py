"""
Shared model mixins for RoadAid Network.
"""
import uuid
from django.db import models


class UUIDMixin(models.Model):
    """
    Mixin that provides a UUID primary key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """
    Mixin that provides created_at and updated_at timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    Mixin that provides soft delete functionality.
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark the object as deleted without removing from database."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


class BaseModel(UUIDMixin, TimestampMixin):
    """
    Base model combining UUID and timestamp mixins.
    Most models should inherit from this.
    """
    class Meta:
        abstract = True
