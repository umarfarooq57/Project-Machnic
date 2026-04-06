"""
Notification services for RoadAid Network.
Handles push notifications via Firebase Cloud Messaging.
"""
import logging
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


def get_firebase_app():
    """
    Initialize and return Firebase app.
    Returns None if Firebase is not configured.
    """
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        if not hasattr(firebase_admin, '_apps') or not firebase_admin._apps:
            cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', '')
            if cred_path:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                logger.warning("Firebase credentials not configured.")
                return None
        
        return firebase_admin.get_app()
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        return None


def send_push_notification(
    user,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
    save_notification: bool = True
) -> bool:
    """
    Send a push notification to a user.
    
    Args:
        user: User to send notification to
        title: Notification title
        body: Notification body
        data: Additional data payload
        save_notification: Whether to save as in-app notification
    
    Returns:
        True if sent successfully, False otherwise
    """
    from .models import Notification
    
    # Save in-app notification
    if save_notification:
        notification_type = data.get('type', Notification.NotificationType.SYSTEM) if data else Notification.NotificationType.SYSTEM
        Notification.objects.create(
            user=user,
            title=title,
            body=body,
            notification_type=notification_type,
            data=data or {}
        )
    
    # Send push notification if FCM token exists
    if not user.fcm_token:
        logger.info(f"No FCM token for user {user.id}, skipping push notification.")
        return False
    
    try:
        from firebase_admin import messaging
        
        app = get_firebase_app()
        if not app:
            return False
        
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={k: str(v) for k, v in (data or {}).items()},
            token=user.fcm_token,
        )
        
        response = messaging.send(message)
        logger.info(f"Successfully sent push notification: {response}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send push notification: {e}")
        return False


def send_new_request_notification(request):
    """
    Send notification about a new service request to nearby helpers.
    """
    from apps.helpers.services import find_nearby_helpers
    
    helpers = find_nearby_helpers(
        latitude=request.user_latitude,
        longitude=request.user_longitude,
        vehicle_type_id=request.vehicle_type_id
    )
    
    for helper_info in helpers:
        helper = helper_info['helper']
        distance = helper_info['distance_km']
        
        send_push_notification(
            user=helper.user,
            title="New Assistance Request",
            body=f"A user {distance:.1f}km away needs help with their {request.vehicle_type.name}!",
            data={
                'type': 'new_request',
                'request_id': str(request.id),
                'distance_km': str(distance)
            }
        )


def send_request_accepted_notification(request):
    """Send notification that request was accepted."""
    send_push_notification(
        user=request.user,
        title="Helper Found!",
        body=f"{request.helper.user.full_name} has accepted your request and is on the way!",
        data={
            'type': 'request_accepted',
            'request_id': str(request.id),
            'helper_id': str(request.helper.id)
        }
    )


def send_helper_arrived_notification(request):
    """Send notification that helper has arrived."""
    send_push_notification(
        user=request.user,
        title="Helper Arrived",
        body=f"{request.helper.user.full_name} has arrived at your location!",
        data={
            'type': 'helper_arrived',
            'request_id': str(request.id)
        }
    )


def send_service_completed_notification(request):
    """Send notification that service is completed."""
    # Notify user
    send_push_notification(
        user=request.user,
        title="Service Completed",
        body=f"Your service has been completed. Please rate your experience!",
        data={
            'type': 'service_completed',
            'request_id': str(request.id)
        }
    )
    
    # Notify helper
    send_push_notification(
        user=request.helper.user,
        title="Job Completed",
        body=f"Great job! Please wait for payment and rating.",
        data={
            'type': 'service_completed',
            'request_id': str(request.id)
        }
    )
