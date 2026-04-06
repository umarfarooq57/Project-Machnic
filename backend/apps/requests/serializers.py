"""
Service Request serializers.
"""
from rest_framework import serializers
from apps.users.serializers import UserPublicSerializer
from apps.helpers.serializers import HelperPublicSerializer, VehicleTypeSerializer, ServiceTypeSerializer
from .models import ServiceRequest, RequestImage, RequestStatusHistory


class RequestImageSerializer(serializers.ModelSerializer):
    """
    Serializer for request images.
    """
    class Meta:
        model = RequestImage
        fields = ['id', 'image', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class RequestStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for status history.
    """
    changed_by_name = serializers.CharField(source='changed_by.full_name', read_only=True)
    
    class Meta:
        model = RequestStatusHistory
        fields = ['id', 'status', 'changed_by', 'changed_by_name', 'notes', 'created_at']


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new service request.
    """
    service_type_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ServiceRequest
        fields = [
            'vehicle_type', 'service_type_ids', 'issue_description', 'urgency',
            'user_latitude', 'user_longitude', 'user_address',
            'is_barter', 'barter_terms', 'images'
        ]

    def validate(self, attrs):
        # Validate coordinates
        lat = attrs.get('user_latitude')
        lon = attrs.get('user_longitude')
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise serializers.ValidationError("Invalid coordinates")
        return attrs

    def create(self, validated_data):
        service_type_ids = validated_data.pop('service_type_ids', [])
        images = validated_data.pop('images', [])
        
        request = ServiceRequest.objects.create(
            user=self.context['request'].user,
            status=ServiceRequest.Status.SEARCHING,
            **validated_data
        )
        
        # Set service types
        if service_type_ids:
            from apps.helpers.models import ServiceType
            service_types = ServiceType.objects.filter(id__in=service_type_ids)
            request.service_types.set(service_types)
        
        # Create images
        for image in images:
            RequestImage.objects.create(request=request, image=image)
        
        return request


class ServiceRequestSerializer(serializers.ModelSerializer):
    """
    Full serializer for service requests.
    """
    user = UserPublicSerializer(read_only=True)
    helper = HelperPublicSerializer(read_only=True)
    vehicle_type = VehicleTypeSerializer(read_only=True)
    service_types = ServiceTypeSerializer(many=True, read_only=True)
    images = RequestImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'user', 'helper', 'vehicle_type', 'service_types',
            'issue_description', 'urgency', 'status',
            'user_latitude', 'user_longitude', 'user_address',
            'helper_latitude', 'helper_longitude',
            'eta_minutes', 'estimated_price', 'final_price',
            'is_barter', 'barter_terms', 'images',
            'accepted_at', 'arrived_at', 'started_at', 'completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'helper', 'status', 'created_at', 'updated_at']


class ServiceRequestListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for request lists.
    """
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    helper_name = serializers.CharField(source='helper.user.full_name', read_only=True)
    vehicle_type_name = serializers.CharField(source='vehicle_type.name', read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'user_name', 'helper_name', 'vehicle_type_name',
            'status', 'urgency', 'eta_minutes',
            'user_latitude', 'user_longitude',
            'created_at'
        ]


class AcceptRequestSerializer(serializers.Serializer):
    """
    Serializer for accepting a request.
    """
    pass  # No input needed, helper is from auth


class UpdateRequestStatusSerializer(serializers.Serializer):
    """
    Serializer for updating request status.
    """
    status = serializers.ChoiceField(choices=[
        ServiceRequest.Status.EN_ROUTE,
        ServiceRequest.Status.ARRIVED,
        ServiceRequest.Status.IN_PROGRESS,
        ServiceRequest.Status.COMPLETED,
    ])
    notes = serializers.CharField(required=False, allow_blank=True)
    final_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False
    )


class CancelRequestSerializer(serializers.Serializer):
    """
    Serializer for cancelling a request.
    """
    reason = serializers.CharField(required=False, allow_blank=True)


class HelperLocationUpdateSerializer(serializers.Serializer):
    """
    Serializer for helper location updates during en-route.
    """
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
