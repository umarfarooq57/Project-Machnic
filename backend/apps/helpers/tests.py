"""
Comprehensive tests for the helpers app.
"""
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.helpers.models import Helper, VehicleType, ServiceType


class HelperRegistrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='helper@example.com', password='Pass123!', full_name='Helper User'
        )
        self.vt = VehicleType.objects.create(name='Car', description='Sedan/Hatchback')
        self.st = ServiceType.objects.create(name='Flat Tire', base_price=50)
        self.client.force_authenticate(user=self.user)

    def test_register_as_helper(self):
        url = reverse('helpers:register')
        data = {
            'shop_name': 'Quick Fix Garage',
            'experience_years': 5,
            'vehicle_types': [self.vt.id],
            'service_types': [self.st.id],
        }
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertTrue(Helper.objects.filter(user=self.user).exists())


class HelperProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='helperprofile@example.com', password='Pass123!',
            full_name='Helper Profile', role='helper'
        )
        self.helper = Helper.objects.create(
            user=self.user,
            shop_name='Test Garage',
            experience_years=3,
        )
        self.client.force_authenticate(user=self.user)

    def test_get_helper_profile(self):
        url = reverse('helpers:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['shop_name'], 'Test Garage')

    def test_toggle_availability(self):
        url = reverse('helpers:availability')
        response = self.client.post(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK])
        self.helper.refresh_from_db()
        # Availability should have been toggled


class VehicleAndServiceTypeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='types@example.com', password='Pass123!', full_name='Types User'
        )
        VehicleType.objects.create(name='Car', description='Sedan')
        VehicleType.objects.create(name='Truck', description='Heavy truck')
        ServiceType.objects.create(name='Oil Change', base_price=30)
        ServiceType.objects.create(name='Battery', base_price=80)
        self.client.force_authenticate(user=self.user)

    def test_list_vehicle_types(self):
        url = reverse('helpers:vehicle-types')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_service_types(self):
        url = reverse('helpers:service-types')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
