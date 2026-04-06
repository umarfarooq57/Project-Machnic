"""
Seed data script for RoadAid Network.
Run with: python manage.py shell < seed_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roadaid.settings')
django.setup()

from apps.helpers.models import VehicleType, ServiceType

# Create Vehicle Types
vehicle_types = [
    {'name': 'Motorcycle', 'icon': '🏍️', 'base_price': 500, 'price_multiplier': 0.8, 'description': 'Bikes and scooters'},
    {'name': 'Car', 'icon': '🚗', 'base_price': 1000, 'price_multiplier': 1.0, 'description': 'Sedan, hatchback, SUV'},
    {'name': 'Rickshaw', 'icon': '🛺', 'base_price': 600, 'price_multiplier': 0.9, 'description': 'Auto rickshaw'},
    {'name': 'Truck', 'icon': '🚛', 'base_price': 2000, 'price_multiplier': 1.5, 'description': 'Trucks and commercial vehicles'},
    {'name': 'Bus', 'icon': '🚌', 'base_price': 2500, 'price_multiplier': 1.8, 'description': 'Buses and coaches'},
]

print("Creating VehicleTypes...")
for vt in vehicle_types:
    obj, created = VehicleType.objects.get_or_create(name=vt['name'], defaults=vt)
    print(f"  {'Created' if created else 'Exists'}: {vt['name']}")

# Create Service Types
service_types = [
    {'name': 'Tire Change', 'icon': '🔧', 'description': 'Flat tire repair/replacement', 'estimated_duration_minutes': 30},
    {'name': 'Battery Jump', 'icon': '🔋', 'description': 'Battery jump start', 'estimated_duration_minutes': 15},
    {'name': 'Fuel Delivery', 'icon': '⛽', 'description': 'Emergency fuel delivery', 'estimated_duration_minutes': 45},
    {'name': 'Engine Repair', 'icon': '🔩', 'description': 'Basic engine troubleshooting', 'estimated_duration_minutes': 60},
    {'name': 'Towing', 'icon': '🚗', 'description': 'Vehicle towing service', 'estimated_duration_minutes': 90},
    {'name': 'Lockout', 'icon': '🔑', 'description': 'Locked out of vehicle', 'estimated_duration_minutes': 20},
]

print("\nCreating ServiceTypes...")
for st in service_types:
    obj, created = ServiceType.objects.get_or_create(name=st['name'], defaults=st)
    print(f"  {'Created' if created else 'Exists'}: {st['name']}")

print(f"\n✅ Seed data complete!")
print(f"VehicleTypes: {VehicleType.objects.count()}")
print(f"ServiceTypes: {ServiceType.objects.count()}")

# Create Service Locations
from apps.helpers.models import ServiceLocation

locations = [
    {
        'name': 'All Pakistan',
        'name_urdu': 'پورا پاکستان',
        'code': 'PKN',
        'latitude': 30.3753,
        'longitude': 69.3451,
        'radius_km': 2000,
        'is_nationwide': True,
        'display_order': 0
    },
    {
        'name': 'Lahore',
        'name_urdu': 'لاہور',
        'code': 'LHR',
        'latitude': 31.5204,
        'longitude': 74.3587,
        'radius_km': 50,
        'is_nationwide': False,
        'display_order': 1
    },
    {
        'name': 'Karachi',
        'name_urdu': 'کراچی',
        'code': 'KHI',
        'latitude': 24.8607,
        'longitude': 67.0011,
        'radius_km': 60,
        'is_nationwide': False,
        'display_order': 2
    },
    {
        'name': 'Islamabad',
        'name_urdu': 'اسلام آباد',
        'code': 'ISB',
        'latitude': 33.6844,
        'longitude': 73.0479,
        'radius_km': 40,
        'is_nationwide': False,
        'display_order': 3
    },
    {
        'name': 'Rawalpindi',
        'name_urdu': 'راولپنڈی',
        'code': 'RWP',
        'latitude': 33.5651,
        'longitude': 73.0169,
        'radius_km': 35,
        'is_nationwide': False,
        'display_order': 4
    },
]

print("\nCreating ServiceLocations...")
for loc in locations:
    try:
        obj, created = ServiceLocation.objects.get_or_create(code=loc['code'], defaults=loc)
        print(f"  {'Created' if created else 'Exists'}: {loc['name']}")
    except Exception as e:
        print(f"  Skipped {loc['name']}: Model may not exist yet")

print(f"\nServiceLocations: {ServiceLocation.objects.count()}")

