"""
Shared utility functions for RoadAid Network.
"""
import math
from typing import Tuple, Optional


def calculate_distance(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float
) -> float:
    """
    Calculate the distance between two coordinates using Haversine formula.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
    
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def calculate_eta(
    distance_km: float, 
    avg_speed_kmh: float = 30.0
) -> int:
    """
    Calculate estimated time of arrival in minutes.
    
    Args:
        distance_km: Distance in kilometers
        avg_speed_kmh: Average speed in km/h (default 30 for city traffic)
    
    Returns:
        ETA in minutes
    """
    if avg_speed_kmh <= 0:
        return 0
    return int((distance_km / avg_speed_kmh) * 60)


def calculate_price(
    base_price: float,
    distance_km: float,
    surge_multiplier: float = 1.0,
    vehicle_type_multiplier: float = 1.0
) -> float:
    """
    Calculate service price based on distance and various factors.
    
    Args:
        base_price: Base price for the service
        distance_km: Distance in kilometers
        surge_multiplier: Surge pricing multiplier (1.0 = no surge)
        vehicle_type_multiplier: Multiplier based on vehicle type
    
    Returns:
        Calculated price
    """
    # Price per km (can be configured)
    per_km_rate = 2.0
    
    distance_charge = distance_km * per_km_rate
    total = (base_price + distance_charge) * surge_multiplier * vehicle_type_multiplier
    
    # Round to 2 decimal places
    return round(total, 2)


def format_phone_number(phone: str) -> str:
    """
    Normalize phone number format.
    Removes spaces, dashes, and ensures proper format.
    
    Args:
        phone: Raw phone number string
    
    Returns:
        Normalized phone number
    """
    # Remove common separators
    cleaned = ''.join(char for char in phone if char.isdigit() or char == '+')
    return cleaned


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate if coordinates are within valid ranges.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        True if valid, False otherwise
    """
    return -90 <= lat <= 90 and -180 <= lon <= 180


def get_bounding_box(
    lat: float, 
    lon: float, 
    radius_km: float
) -> Tuple[float, float, float, float]:
    """
    Get bounding box coordinates for a given center point and radius.
    Useful for database queries to find nearby helpers.
    
    Args:
        lat: Center latitude
        lon: Center longitude
        radius_km: Radius in kilometers
    
    Returns:
        Tuple of (min_lat, max_lat, min_lon, max_lon)
    """
    # Approximate degrees per km
    lat_diff = radius_km / 111.0  # ~111 km per degree latitude
    lon_diff = radius_km / (111.0 * math.cos(math.radians(lat)))
    
    return (
        lat - lat_diff,  # min_lat
        lat + lat_diff,  # max_lat
        lon - lon_diff,  # min_lon
        lon + lon_diff   # max_lon
    )
