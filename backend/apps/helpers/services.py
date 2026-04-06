"""
Geolocation services for finding nearby helpers.
"""
from typing import List, Optional
from django.conf import settings
from django.db.models import QuerySet
from core.utils import calculate_distance, calculate_eta, get_bounding_box
from .models import Helper


def find_nearby_helpers(
    latitude: float,
    longitude: float,
    radius_km: float = None,
    vehicle_type_id: int = None,
    service_type_id: int = None,
    limit: int = None
) -> List[dict]:
    """
    Find available helpers near a given location.
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        radius_km: Search radius in kilometers (default from settings)
        vehicle_type_id: Filter by vehicle type
        service_type_id: Filter by service type
        limit: Maximum number of helpers to return
    
    Returns:
        List of helper dicts with distance and ETA info
    """
    if radius_km is None:
        radius_km = getattr(settings, 'HELPER_SEARCH_RADIUS_KM', 10)
    
    if limit is None:
        limit = getattr(settings, 'MAX_HELPERS_TO_NOTIFY', 10)
    
    # Get bounding box for initial filtering
    min_lat, max_lat, min_lon, max_lon = get_bounding_box(latitude, longitude, radius_km)
    
    # Base queryset - available, verified helpers
    queryset = Helper.objects.filter(
        is_available=True,
        verification_status=Helper.VerificationStatus.VERIFIED,
        user__is_active=True,
        user__latitude__gte=min_lat,
        user__latitude__lte=max_lat,
        user__longitude__gte=min_lon,
        user__longitude__lte=max_lon,
    ).select_related('user')
    
    # Filter by vehicle type if specified
    if vehicle_type_id:
        queryset = queryset.filter(vehicle_types__id=vehicle_type_id)
    
    # Filter by service type if specified
    if service_type_id:
        queryset = queryset.filter(service_types__id=service_type_id)
    
    # Calculate distances and filter by exact radius
    helpers_with_distance = []
    for helper in queryset:
        if helper.user.latitude is None or helper.user.longitude is None:
            continue
            
        distance = calculate_distance(
            latitude, longitude,
            helper.user.latitude, helper.user.longitude
        )
        
        # Check if within the helper's own service radius too
        if distance <= radius_km and distance <= helper.service_radius_km:
            eta = calculate_eta(distance)
            helpers_with_distance.append({
                'helper': helper,
                'distance_km': round(distance, 2),
                'eta_minutes': eta
            })
    
    # Sort by distance and limit
    helpers_with_distance.sort(key=lambda x: x['distance_km'])
    return helpers_with_distance[:limit]


def get_helper_by_distance(
    helpers: QuerySet[Helper],
    latitude: float,
    longitude: float
) -> Helper:
    """
    Get the closest helper from a queryset.
    
    Args:
        helpers: QuerySet of helpers to search
        latitude: Target latitude
        longitude: Target longitude
    
    Returns:
        The closest helper or None
    """
    closest_helper = None
    min_distance = float('inf')
    
    for helper in helpers:
        if helper.user.latitude is None or helper.user.longitude is None:
            continue
            
        distance = calculate_distance(
            latitude, longitude,
            helper.user.latitude, helper.user.longitude
        )
        
        if distance < min_distance:
            min_distance = distance
            closest_helper = helper
    
    return closest_helper


def notify_nearby_helpers(
    latitude: float,
    longitude: float,
    request_id: str,
    vehicle_type_id: int = None
) -> int:
    """
    Send notifications to nearby available helpers about a new request.
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        request_id: ID of the service request
        vehicle_type_id: Filter by vehicle type
    
    Returns:
        Number of helpers notified
    """
    from apps.notifications.services import send_push_notification
    
    nearby_helpers = find_nearby_helpers(
        latitude=latitude,
        longitude=longitude,
        vehicle_type_id=vehicle_type_id
    )
    
    notified_count = 0
    for helper_info in nearby_helpers:
        helper = helper_info['helper']
        distance = helper_info['distance_km']
        
        if helper.user.fcm_token:
            send_push_notification(
                user=helper.user,
                title="New Service Request",
                body=f"A user {distance:.1f}km away needs assistance!",
                data={
                    'type': 'new_request',
                    'request_id': str(request_id),
                    'distance_km': distance
                }
            )
            notified_count += 1
    
    return notified_count
