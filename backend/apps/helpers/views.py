"""
Helper views for profile and availability management.
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.users.permissions import IsHelper
from .models import Helper, VehicleType, ServiceType, HelperSchedule, ServiceLocation
from .serializers import (
    HelperSerializer,
    HelperPublicSerializer,
    HelperRegistrationSerializer,
    HelperAvailabilitySerializer,
    HelperScheduleSerializer,
    VehicleTypeSerializer,
    ServiceTypeSerializer,
    NearbyHelpersRequestSerializer,
    ServiceLocationSerializer,
)
from .services import find_nearby_helpers



@extend_schema(tags=['Helpers'])
class HelperRegistrationView(generics.CreateAPIView):
    """
    Register as a helper/mechanic.
    Creates a helper profile for the authenticated user.
    """
    serializer_class = HelperRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check if user already has a helper profile
        if hasattr(request.user, 'helper_profile'):
            return Response(
                {'error': 'You already have a helper profile.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        helper = serializer.save()
        
        return Response({
            'message': 'Helper profile created successfully. Pending verification.',
            'helper': HelperSerializer(helper).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Helpers'])
class HelperProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current user's helper profile.
    """
    serializer_class = HelperSerializer
    permission_classes = [permissions.IsAuthenticated, IsHelper]

    def get_object(self):
        return self.request.user.helper_profile


@extend_schema(tags=['Helpers'])
class HelperDetailView(generics.RetrieveAPIView):
    """
    Get a specific helper's public profile.
    """
    queryset = Helper.objects.select_related('user').filter(
        verification_status=Helper.VerificationStatus.VERIFIED,
        user__is_active=True
    )
    serializer_class = HelperPublicSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=['Helpers'])
class HelperAvailabilityView(APIView):
    """
    Toggle or set helper availability status.
    """
    permission_classes = [permissions.IsAuthenticated, IsHelper]

    def get(self, request):
        """Get current availability status."""
        helper = request.user.helper_profile
        return Response({
            'is_available': helper.is_available,
            'is_online': helper.is_online,
            'last_online': helper.last_online
        })

    def post(self, request):
        """Update availability status."""
        serializer = HelperAvailabilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        helper = request.user.helper_profile
        helper.toggle_availability(serializer.validated_data['is_available'])
        
        return Response({
            'message': 'Availability updated.',
            'is_available': helper.is_available,
            'is_online': helper.is_online
        })


@extend_schema(tags=['Helpers'])
class NearbyHelpersView(APIView):
    """
    Find available helpers near a location.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = NearbyHelpersRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        helpers_data = find_nearby_helpers(
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            radius_km=serializer.validated_data.get('radius_km', 10),
            vehicle_type_id=serializer.validated_data.get('vehicle_type_id'),
            service_type_id=serializer.validated_data.get('service_type_id'),
        )
        
        # Serialize with distance/eta info
        results = []
        for item in helpers_data:
            helper_data = HelperPublicSerializer(item['helper']).data
            helper_data['distance_km'] = item['distance_km']
            helper_data['eta_minutes'] = item['eta_minutes']
            results.append(helper_data)
        
        return Response({
            'count': len(results),
            'helpers': results
        })


@extend_schema(tags=['Helpers'])
class HelperScheduleListView(generics.ListCreateAPIView):
    """
    List or create helper schedules.
    """
    serializer_class = HelperScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsHelper]

    def get_queryset(self):
        return HelperSchedule.objects.filter(helper=self.request.user.helper_profile)

    def perform_create(self, serializer):
        serializer.save(helper=self.request.user.helper_profile)


@extend_schema(tags=['Helpers'])
class HelperScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific schedule.
    """
    serializer_class = HelperScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsHelper]

    def get_queryset(self):
        return HelperSchedule.objects.filter(helper=self.request.user.helper_profile)


@extend_schema(tags=['Configuration'])
class VehicleTypeListView(generics.ListAPIView):
    """
    List all available vehicle types.
    """
    queryset = VehicleType.objects.filter(is_active=True)
    serializer_class = VehicleTypeSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=['Configuration'])
class ServiceTypeListView(generics.ListAPIView):
    """
    List all available service types.
    """
    queryset = ServiceType.objects.filter(is_active=True)
    serializer_class = ServiceTypeSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=['Configuration'])
class ServiceLocationListView(generics.ListAPIView):
    """
    List all available service locations/cities.
    """
    queryset = ServiceLocation.objects.filter(is_active=True)
    serializer_class = ServiceLocationSerializer
    permission_classes = [permissions.AllowAny]

