"""
Service Request views.
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from apps.users.permissions import IsHelper, IsRequestParticipant
from core.exceptions import RequestAlreadyAccepted, InvalidRequestStatus
from .models import ServiceRequest, RequestStatusHistory
from .serializers import (
    ServiceRequestCreateSerializer,
    ServiceRequestSerializer,
    ServiceRequestListSerializer,
    AcceptRequestSerializer,
    UpdateRequestStatusSerializer,
    CancelRequestSerializer,
    HelperLocationUpdateSerializer,
    RequestStatusHistorySerializer,
)


@extend_schema(tags=['Requests'])
class CreateRequestView(generics.CreateAPIView):
    """
    Create a new service request.
    Automatically searches for nearby available helpers.
    """
    serializer_class = ServiceRequestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service_request = serializer.save()
        
        # Notify nearby helpers
        from apps.helpers.services import notify_nearby_helpers
        notified = notify_nearby_helpers(
            latitude=service_request.user_latitude,
            longitude=service_request.user_longitude,
            request_id=service_request.id,
            vehicle_type_id=service_request.vehicle_type_id
        )
        
        # Broadcast to WebSocket
        self._broadcast_new_request(service_request)
        
        return Response({
            'request': ServiceRequestSerializer(service_request).data,
            'helpers_notified': notified
        }, status=status.HTTP_201_CREATED)

    def _broadcast_new_request(self, request):
        """Broadcast new request to nearby helpers via WebSocket."""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'nearby_requests',
            {
                'type': 'new_request',
                'request': ServiceRequestListSerializer(request).data
            }
        )


@extend_schema(tags=['Requests'])
class RequestDetailView(generics.RetrieveAPIView):
    """
    Get detailed information about a specific request.
    """
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsRequestParticipant]
    queryset = ServiceRequest.objects.all()


@extend_schema(tags=['Requests'])
class UserRequestsListView(generics.ListAPIView):
    """
    List all requests for the current user.
    """
    serializer_class = ServiceRequestListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ServiceRequest.objects.filter(user=self.request.user).select_related('helper').prefetch_related('statushistory_set')


@extend_schema(tags=['Requests'])
class HelperRequestsListView(generics.ListAPIView):
    """
    List all requests assigned to the current helper.
    """
    serializer_class = ServiceRequestListSerializer
    permission_classes = [permissions.IsAuthenticated, IsHelper]

    def get_queryset(self):
        return ServiceRequest.objects.filter(helper=self.request.user.helper_profile).select_related('user').prefetch_related('statushistory_set')


@extend_schema(tags=['Requests'])
class AvailableRequestsView(generics.ListAPIView):
    """
    List available requests for helpers to accept.
    """
    serializer_class = ServiceRequestListSerializer
    permission_classes = [permissions.IsAuthenticated, IsHelper]

    def get_queryset(self):
        helper = self.request.user.helper_profile
        
        # Get requests that are searching for helpers
        queryset = ServiceRequest.objects.filter(
            status__in=[ServiceRequest.Status.PENDING, ServiceRequest.Status.SEARCHING],
        )
        
        # Filter by vehicle types the helper can service
        helper_vehicle_types = helper.vehicle_types.values_list('id', flat=True)
        if helper_vehicle_types:
            queryset = queryset.filter(vehicle_type_id__in=helper_vehicle_types)
        
        return queryset


@extend_schema(tags=['Requests'])
class AcceptRequestView(APIView):
    """
    Accept a service request as a helper.
    """
    permission_classes = [permissions.IsAuthenticated, IsHelper]

    def post(self, request, pk):
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        
        if not service_request.can_be_accepted():
            raise RequestAlreadyAccepted()
        
        helper = request.user.helper_profile
        
        try:
            service_request.accept(helper)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Record status change
        RequestStatusHistory.objects.create(
            request=service_request,
            status=ServiceRequest.Status.ACCEPTED,
            changed_by=request.user,
            notes='Request accepted by helper'
        )
        
        # Broadcast update
        self._broadcast_request_update(service_request, 'accepted')
        
        return Response({
            'message': 'Request accepted successfully.',
            'request': ServiceRequestSerializer(service_request).data
        })

    def _broadcast_request_update(self, request, event_type):
        """Broadcast request update via WebSocket."""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        
        # Notify request room
        async_to_sync(channel_layer.group_send)(
            f'request_{request.id}',
            {
                'type': 'request_update',
                'request_id': str(request.id),
                'status': request.status,
                'data': ServiceRequestSerializer(request).data
            }
        )
        
        # Notify other helpers that request is taken
        async_to_sync(channel_layer.group_send)(
            'nearby_requests',
            {
                'type': 'request_taken',
                'request_id': str(request.id)
            }
        )


@extend_schema(tags=['Requests'])
class UpdateRequestStatusView(APIView):
    """
    Update the status of a service request.
    Only the assigned helper can update status.
    """
    permission_classes = [permissions.IsAuthenticated, IsHelper]

    def post(self, request, pk):
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        
        # Verify helper is assigned to this request
        if service_request.helper != request.user.helper_profile:
            return Response(
                {'error': 'You are not assigned to this request.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UpdateRequestStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')
        
        # Update based on new status
        if new_status == ServiceRequest.Status.EN_ROUTE:
            service_request.mark_en_route()
        elif new_status == ServiceRequest.Status.ARRIVED:
            service_request.mark_arrived()
        elif new_status == ServiceRequest.Status.IN_PROGRESS:
            service_request.start_service()
        elif new_status == ServiceRequest.Status.COMPLETED:
            final_price = serializer.validated_data.get('final_price')
            service_request.complete(final_price)
        
        # Record status change
        RequestStatusHistory.objects.create(
            request=service_request,
            status=new_status,
            changed_by=request.user,
            notes=notes
        )
        
        # Broadcast update
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'request_{service_request.id}',
            {
                'type': 'request_update',
                'request_id': str(service_request.id),
                'status': service_request.status,
                'data': ServiceRequestSerializer(service_request).data
            }
        )
        
        return Response({
            'message': f'Status updated to {new_status}.',
            'request': ServiceRequestSerializer(service_request).data
        })


@extend_schema(tags=['Requests'])
class CancelRequestView(APIView):
    """
    Cancel a service request.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        
        # Check if user can cancel (either the requester or assigned helper)
        can_cancel = (
            service_request.user == request.user or
            (service_request.helper and service_request.helper.user == request.user)
        )
        
        if not can_cancel:
            return Response(
                {'error': 'You cannot cancel this request.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if request can be cancelled
        if service_request.status in [
            ServiceRequest.Status.COMPLETED,
            ServiceRequest.Status.CANCELLED
        ]:
            raise InvalidRequestStatus("Cannot cancel a completed or already cancelled request.")
        
        serializer = CancelRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service_request.cancel(
            cancelled_by_user=request.user,
            reason=serializer.validated_data.get('reason', '')
        )
        
        # Record status change
        RequestStatusHistory.objects.create(
            request=service_request,
            status=ServiceRequest.Status.CANCELLED,
            changed_by=request.user,
            notes=f"Cancelled: {serializer.validated_data.get('reason', 'No reason provided')}"
        )
        
        return Response({
            'message': 'Request cancelled successfully.',
            'request': ServiceRequestSerializer(service_request).data
        })


@extend_schema(tags=['Requests'])
class UpdateHelperLocationView(APIView):
    """
    Update helper's location during en-route status.
    Used for real-time ETA updates.
    """
    permission_classes = [permissions.IsAuthenticated, IsHelper]

    def post(self, request, pk):
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        
        # Verify helper is assigned
        if service_request.helper != request.user.helper_profile:
            return Response(
                {'error': 'You are not assigned to this request.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = HelperLocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service_request.update_helper_location(
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude']
        )
        
        # Broadcast location update
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'request_{service_request.id}',
            {
                'type': 'location_broadcast',
                'latitude': serializer.validated_data['latitude'],
                'longitude': serializer.validated_data['longitude'],
                'user_id': str(request.user.id),
                'eta_minutes': service_request.eta_minutes
            }
        )
        
        return Response({
            'message': 'Location updated.',
            'eta_minutes': service_request.eta_minutes,
            'helper_latitude': service_request.helper_latitude,
            'helper_longitude': service_request.helper_longitude
        })


@extend_schema(tags=['Requests'])
class RequestStatusHistoryView(generics.ListAPIView):
    """
    Get the status history for a request.
    """
    serializer_class = RequestStatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated, IsRequestParticipant]

    def get_queryset(self):
        request_id = self.kwargs['pk']
        return RequestStatusHistory.objects.filter(request_id=request_id)
