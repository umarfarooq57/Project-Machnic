"""
SOS / Emergency views for RoadAid Network.
"""
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.notifications.models import Notification
from apps.admin_panel.models import EmergencyContact


@extend_schema(tags=['Safety'])
class TriggerSOSView(APIView):
    """
    Trigger an SOS emergency alert.
    - Creates a high-priority system notification for all admin users.
    - Returns the user's emergency contacts for client-side actions (call/SMS).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        message = request.data.get('message', 'Emergency SOS triggered!')

        # Create admin notification
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_users = User.objects.filter(role='admin', is_active=True)

        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                title='🚨 SOS ALERT',
                body=f'{user.full_name} ({user.email}) triggered SOS! '
                     f'Location: ({latitude}, {longitude}). {message}',
                notification_type=Notification.NotificationType.SYSTEM,
                data={
                    'type': 'sos',
                    'user_id': str(user.id),
                    'latitude': latitude,
                    'longitude': longitude,
                },
            )

        # Also notify via push if we have an active service request
        from apps.requests.models import ServiceRequest
        active_request = ServiceRequest.objects.filter(
            user=user,
            status__in=[
                ServiceRequest.Status.ACCEPTED,
                ServiceRequest.Status.EN_ROUTE,
                ServiceRequest.Status.ARRIVED,
                ServiceRequest.Status.IN_PROGRESS,
            ]
        ).first()

        helper_notified = False
        if active_request and active_request.helper:
            Notification.objects.create(
                user=active_request.helper.user,
                title='🚨 SOS from Customer',
                body=f'{user.full_name} has triggered an SOS alert!',
                notification_type=Notification.NotificationType.SYSTEM,
                request=active_request,
                data={'type': 'sos', 'user_id': str(user.id)},
            )
            helper_notified = True

        # Return emergency contacts so the client can initiate calls/SMS
        contacts = EmergencyContact.objects.filter(user=user).values(
            'name', 'phone', 'relationship'
        )

        return Response({
            'message': 'SOS alert sent to platform administrators.',
            'helper_notified': helper_notified,
            'emergency_contacts': list(contacts),
        }, status=status.HTTP_200_OK)
