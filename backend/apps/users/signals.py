"""
Signals for the users app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User


@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    """
    Handle actions when a new user is created.
    """
    if created:
        # TODO: Send welcome email
        # TODO: Create default notification preferences
        pass
