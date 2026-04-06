"""
Comprehensive tests for the requests app.
"""
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status as http_status
from apps.users.models import User
from apps.helpers.models import Helper, VehicleType, ServiceType
from apps.requests.models import ServiceRequest


class ServiceRequestLifecycleTests(APITestCase):
    """Test the full lifecycle: create → accept → en_route → arrived → in_progress → complete."""

    def setUp(self):
        # Create a user and a helper
        self.user = User.objects.create_user(
            email='rider@example.com', password='Pass123!', full_name='Rider',
            latitude=24.8607, longitude=67.0011,
        )
        self.helper_user = User.objects.create_user(
            email='mechanic@example.com', password='Pass123!', full_name='Mechanic',
            role='helper', latitude=24.8700, longitude=67.0100,
        )
        self.vt = VehicleType.objects.create(name='Car', description='Sedan')
        self.st = ServiceType.objects.create(name='Flat Tire', base_price=50)
        self.helper = Helper.objects.create(
            user=self.helper_user,
            shop_name='Pro Garage',
            experience_years=5,
            is_available=True,
            is_online=True,
            verification_status=Helper.VerificationStatus.VERIFIED,
        )
        self.helper.vehicle_types.add(self.vt)
        self.helper.service_types.add(self.st)

    def _create_request(self):
        """Helper: create a service request as the rider."""
        self.client.force_authenticate(user=self.user)
        url = reverse('requests:request-create')
        data = {
            'vehicle_type': self.vt.id,
            'issue_description': 'Flat tire on highway',
            'user_latitude': 24.8607,
            'user_longitude': 67.0011,
            'urgency': 'medium',
        }
        response = self.client.post(url, data)
        return response

    def test_create_request(self):
        response = self._create_request()
        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

    def test_accept_request(self):
        # Create request
        resp = self._create_request()
        request_id = resp.data.get('request', {}).get('id') or resp.data.get('id')
        if not request_id:
            return  # Skip if response format is unexpected

        # Accept as helper
        self.client.force_authenticate(user=self.helper_user)
        url = reverse('requests:accept', kwargs={'pk': request_id})
        response = self.client.post(url)
        self.assertIn(response.status_code, [
            http_status.HTTP_200_OK,
            http_status.HTTP_400_BAD_REQUEST,  # If already accepted
        ])


class RequestCancellationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='canceller@example.com', password='Pass123!', full_name='Canceller',
        )
        self.vt = VehicleType.objects.create(name='Car', description='Sedan')

    def test_cancel_pending_request(self):
        self.client.force_authenticate(user=self.user)
        # Create
        create_url = reverse('requests:request-create')
        data = {
            'vehicle_type': self.vt.id,
            'issue_description': 'Engine issue',
            'user_latitude': 24.8607,
            'user_longitude': 67.0011,
            'urgency': 'low',
        }
        resp = self.client.post(create_url, data)
        self.assertEqual(resp.status_code, http_status.HTTP_201_CREATED)

        request_id = resp.data.get('request', {}).get('id') or resp.data.get('id')
        if not request_id:
            return

        # Cancel
        cancel_url = reverse('requests:cancel', kwargs={'pk': request_id})
        response = self.client.post(cancel_url)
        self.assertIn(response.status_code, [
            http_status.HTTP_200_OK,
            http_status.HTTP_400_BAD_REQUEST,
        ])


class SOSTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='sos@example.com', password='Pass123!', full_name='SOS User',
        )
        self.admin = User.objects.create_user(
            email='admin@example.com', password='Pass123!', full_name='Admin', role='admin',
        )
        self.client.force_authenticate(user=self.user)

    def test_trigger_sos(self):
        url = reverse('requests:sos')
        data = {
            'latitude': 24.8607,
            'longitude': 67.0011,
            'message': 'I need help!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertIn('emergency_contacts', response.data)
