"""
Comprehensive tests for the admin_panel app.
"""
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.helpers.models import Helper
from apps.admin_panel.models import PromoCode, Dispute, PlatformConfig


class DashboardTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@example.com', password='Pass123!',
            full_name='Admin User', role='admin',
        )
        self.client.force_authenticate(user=self.admin)

    def test_dashboard_stats(self):
        url = reverse('admin-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('total_helpers', response.data)
        self.assertIn('total_revenue', response.data)

    def test_dashboard_not_accessible_to_non_admin(self):
        user = User.objects.create_user(
            email='normie@example.com', password='Pass123!', full_name='Normie',
        )
        self.client.force_authenticate(user=user)
        url = reverse('admin-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revenue_report(self):
        url = reverse('admin-revenue-report')
        response = self.client.get(url, {'days': 7})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PromoCodeTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin2@example.com', password='Pass123!',
            full_name='Admin', role='admin',
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_promo_code(self):
        url = reverse('admin-promo-list')
        data = {
            'code': 'SAVE20',
            'discount_type': 'percentage',
            'discount_value': '20.00',
            'valid_from': timezone.now().isoformat(),
            'valid_until': (timezone.now() + timezone.timedelta(days=30)).isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PromoCode.objects.count(), 1)

    def test_list_promo_codes(self):
        PromoCode.objects.create(
            code='TEST10', discount_type='flat', discount_value=10,
            valid_from=timezone.now(), valid_until=timezone.now() + timezone.timedelta(days=7),
        )
        url = reverse('admin-promo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']) if 'results' in response.data else len(response.data), 1)

    def test_apply_promo_code(self):
        """Test applying a promo code as a regular user."""
        PromoCode.objects.create(
            code='FLAT50', discount_type='flat', discount_value=50,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=30),
        )
        user = User.objects.create_user(
            email='buyer@example.com', password='Pass123!', full_name='Buyer',
        )
        self.client.force_authenticate(user=user)
        url = reverse('promo-apply')
        data = {'code': 'FLAT50', 'order_amount': '200.00'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['discount_amount'], '50.00')
        self.assertEqual(response.data['final_amount'], '150.00')


class HelperVerificationTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin3@example.com', password='Pass123!',
            full_name='Admin', role='admin',
        )
        self.helper_user = User.objects.create_user(
            email='pending@example.com', password='Pass123!', full_name='Pending Helper',
        )
        self.helper = Helper.objects.create(
            user=self.helper_user,
            shop_name='Pending Garage',
            experience_years=2,
            verification_status=Helper.VerificationStatus.PENDING,
        )
        self.client.force_authenticate(user=self.admin)

    def test_list_pending_helpers(self):
        url = reverse('admin-helper-list')
        response = self.client.get(url, {'verification_status': 'pending'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_helper(self):
        url = reverse('admin-helper-verify', kwargs={'pk': self.helper.pk})
        response = self.client.post(url, {'action': 'approve'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.helper.refresh_from_db()
        self.assertEqual(self.helper.verification_status, 'verified')

    def test_reject_helper(self):
        url = reverse('admin-helper-verify', kwargs={'pk': self.helper.pk})
        response = self.client.post(url, {'action': 'reject'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.helper.refresh_from_db()
        self.assertEqual(self.helper.verification_status, 'rejected')


class EmergencyContactTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='contacts@example.com', password='Pass123!', full_name='Contact User',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_emergency_contact(self):
        url = reverse('emergency-contact-list')
        data = {'name': 'Mom', 'phone': '+1234567890', 'relationship': 'Mother'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_emergency_contacts(self):
        url = reverse('emergency-contact-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
