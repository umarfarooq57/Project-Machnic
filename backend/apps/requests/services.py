"""
Smart Matching and Dynamic Pricing services for RoadAid Network.
"""
from decimal import Decimal
from typing import Optional
from django.db.models import Avg, Count
from django.conf import settings
from core.utils import calculate_distance, calculate_eta
from apps.helpers.models import Helper
from apps.helpers.services import find_nearby_helpers
from apps.admin_panel.models import PlatformConfig


def smart_match_helper(
    latitude: float,
    longitude: float,
    vehicle_type_id: int = None,
    service_type_id: int = None,
    radius_km: float = None,
) -> Optional[dict]:
    """
    Find the best helper using a weighted scoring algorithm.

    Weights:
      - Distance (40%): closer is better
      - Rating (25%): higher is better
      - Specialty match (20%): bonus if helper specialises in the vehicle/service
      - Response history (15%): more completed jobs = more reliable

    Returns:
        Best-matching helper dict or None
    """
    nearby = find_nearby_helpers(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        vehicle_type_id=vehicle_type_id,
        service_type_id=service_type_id,
        limit=20,  # score a larger pool
    )

    if not nearby:
        return None

    max_distance = max(h['distance_km'] for h in nearby) or 1
    max_jobs = max(h['helper'].total_jobs for h in nearby) or 1

    scored = []
    for item in nearby:
        helper = item['helper']
        distance_km = item['distance_km']

        # Normalised scores  (0-1, higher = better)
        distance_score = 1 - (distance_km / max_distance) if max_distance > 0 else 1
        rating_score = (helper.rating_avg or 0) / 5.0
        job_score = helper.total_jobs / max_jobs if max_jobs > 0 else 0

        # Specialty bonus
        specialty_score = 0.0
        if vehicle_type_id and helper.vehicle_types.filter(id=vehicle_type_id).exists():
            specialty_score += 0.5
        if service_type_id and helper.service_types.filter(id=service_type_id).exists():
            specialty_score += 0.5

        total = (
            0.40 * distance_score +
            0.25 * rating_score +
            0.20 * specialty_score +
            0.15 * job_score
        )

        scored.append({**item, 'score': round(total, 4)})

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[0] if scored else None


def calculate_dynamic_price(
    base_price: float,
    distance_km: float,
    vehicle_type_multiplier: float = 1.0,
) -> Decimal:
    """
    Calculate dynamic price factoring in distance, vehicle type, and surge.

    Formula:
        final = base_price × vehicle_multiplier × distance_factor × surge_multiplier

    Distance factor: 1.0 for ≤ 5 km, +0.1 per additional km (capped at 2.0).
    Surge is read from PlatformConfig; defaults to 1.0.
    """
    base = Decimal(str(base_price))
    v_mult = Decimal(str(vehicle_type_multiplier))

    # Distance factor
    if distance_km <= 5:
        d_factor = Decimal('1.0')
    else:
        d_factor = Decimal('1.0') + Decimal(str(min((distance_km - 5) * 0.1, 1.0)))

    # Surge from config
    surge_str = PlatformConfig.get('surge_multiplier', '1.0')
    surge = Decimal(surge_str)

    final = (base * v_mult * d_factor * surge).quantize(Decimal('0.01'))
    return final
