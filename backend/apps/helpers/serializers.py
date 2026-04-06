"""
Helper serializers for profile and availability management.
"""
from rest_framework import serializers
from apps.users.serializers import UserSerializer, UserPublicSerializer
from .models import Helper, VehicleType, ServiceType, HelperSchedule, ServiceLocation


class ServiceLocationSerializer(serializers.ModelSerializer):
    """
    Serializer for service locations/cities.
    """
    class Meta:
        model = ServiceLocation
        fields = ['id', 'name', 'name_urdu', 'code', 'latitude', 'longitude', 'radius_km', 'is_nationwide']


class VehicleTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for vehicle types.
    """
    class Meta:
        model = VehicleType
        fields = ['id', 'name', 'icon', 'base_price', 'price_multiplier', 'description']


class ServiceTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for service types.
    """
    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'description', 'icon', 'estimated_duration_minutes']


class HelperScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for helper schedules.
    """
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = HelperSchedule
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_active']


class HelperSerializer(serializers.ModelSerializer):
    """
    Full helper serializer for profile view/edit.
    """
    user = UserSerializer(read_only=True)
    vehicle_types = VehicleTypeSerializer(many=True, read_only=True)
    vehicle_type_ids = serializers.PrimaryKeyRelatedField(
        queryset=VehicleType.objects.all(),
        many=True,
        write_only=True,
        source='vehicle_types'
    )
    service_types = ServiceTypeSerializer(many=True, read_only=True)
    service_type_ids = serializers.PrimaryKeyRelatedField(
        queryset=ServiceType.objects.all(),
        many=True,
        write_only=True,
        source='service_types'
    )
    schedules = HelperScheduleSerializer(many=True, read_only=True)
    is_verified = serializers.ReadOnlyField()
    
    class Meta:
        model = Helper
        fields = [
            'id', 'user', 'license_number', 'bio', 'years_experience',
            'vehicle_types', 'vehicle_type_ids', 'service_types', 'service_type_ids',
            'is_available', 'is_online', 'service_radius_km',
            'rating_avg', 'rating_count', 'total_jobs',
            'verification_status', 'is_verified', 'schedules',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'rating_avg', 'rating_count', 'total_jobs',
            'verification_status', 'created_at', 'updated_at'
        ]


class HelperPublicSerializer(serializers.ModelSerializer):
    """
    Public helper serializer (for users to see).
    """
    user = UserPublicSerializer(read_only=True)
    vehicle_types = VehicleTypeSerializer(many=True, read_only=True)
    service_types = ServiceTypeSerializer(many=True, read_only=True)
    distance_km = serializers.FloatField(read_only=True, required=False)
    eta_minutes = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Helper
        fields = [
            'id', 'user', 'bio', 'years_experience',
            'vehicle_types', 'service_types',
            'rating_avg', 'rating_count', 'total_jobs',
            'distance_km', 'eta_minutes'
        ]


class HelperRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for helper registration.
    """
    vehicle_type_ids = serializers.PrimaryKeyRelatedField(
        queryset=VehicleType.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    service_type_ids = serializers.PrimaryKeyRelatedField(
        queryset=ServiceType.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Helper
        fields = [
            'license_number', 'bio', 'years_experience',
            'vehicle_type_ids', 'service_type_ids',
            'service_radius_km', 'id_document', 'license_document'
        ]

    def create(self, validated_data):
        vehicle_types = validated_data.pop('vehicle_type_ids', [])
        service_types = validated_data.pop('service_type_ids', [])
        
        user = self.context['request'].user
        helper = Helper.objects.create(user=user, **validated_data)
        
        if vehicle_types:
            helper.vehicle_types.set(vehicle_types)
        if service_types:
            helper.service_types.set(service_types)
        
        # Update user role
        user.role = 'helper'
        user.save(update_fields=['role'])
        
        return helper


class HelperAvailabilitySerializer(serializers.Serializer):
    """
    Serializer for toggling helper availability.
    """
    is_available = serializers.BooleanField()


class NearbyHelpersRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting nearby helpers.
    """
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    vehicle_type_id = serializers.IntegerField(required=False)
    service_type_id = serializers.IntegerField(required=False)
    radius_km = serializers.FloatField(min_value=1, max_value=50, default=10)
