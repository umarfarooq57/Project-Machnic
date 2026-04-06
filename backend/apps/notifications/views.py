"""
Notification and Rating views.
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from .models import Notification, Rating
from .serializers import NotificationSerializer, RatingSerializer, RatingCreateSerializer


@extend_schema(tags=['Notifications'])
class NotificationListView(generics.ListAPIView):
    """
    List all notifications for the current user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@extend_schema(tags=['Notifications'])
class UnreadNotificationsView(generics.ListAPIView):
    """
    List unread notifications for the current user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_read=False)


@extend_schema(tags=['Notifications'])
class MarkNotificationReadView(APIView):
    """
    Mark a notification as read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        notification = get_object_or_404(
            Notification, 
            pk=pk, 
            user=request.user
        )
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read.'})


@extend_schema(tags=['Notifications'])
class MarkAllNotificationsReadView(APIView):
    """
    Mark all notifications as read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from django.utils import timezone
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({'marked_read': updated})


@extend_schema(tags=['Ratings'])
class CreateRatingView(generics.CreateAPIView):
    """
    Create a rating for a completed service request.
    """
    serializer_class = RatingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        from apps.requests.models import ServiceRequest
        
        request_id = self.kwargs['request_id']
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Validate request is completed
        if service_request.status != ServiceRequest.Status.COMPLETED:
            return Response(
                {'error': 'Can only rate completed requests.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine who is being rated
        if service_request.user == request.user:
            # User is rating the helper
            if not service_request.helper:
                return Response(
                    {'error': 'No helper to rate.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            rated_user = service_request.helper.user
        elif service_request.helper and service_request.helper.user == request.user:
            # Helper is rating the user
            rated_user = service_request.user
        else:
            return Response(
                {'error': 'You are not a participant in this request.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if already rated
        if Rating.objects.filter(request=service_request, rater=request.user).exists():
            return Response(
                {'error': 'You have already rated this request.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        rating = Rating.objects.create(
            request=service_request,
            rater=request.user,
            rated_user=rated_user,
            **serializer.validated_data
        )
        
        return Response(
            RatingSerializer(rating).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['Ratings'])
class RequestRatingsView(generics.ListAPIView):
    """
    List all ratings for a request.
    """
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        request_id = self.kwargs['request_id']
        return Rating.objects.filter(request_id=request_id)


@extend_schema(tags=['Ratings'])
class UserRatingsView(generics.ListAPIView):
    """
    List all ratings received by the current user.
    """
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(rated_user=self.request.user)
