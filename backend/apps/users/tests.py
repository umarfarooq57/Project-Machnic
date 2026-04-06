"""
Comprehensive tests for the users app.
"""
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User, UserVerification


class AuthTests(APITestCase):
    def test_register_success(self):
        """Test that user registration works and returns JWT tokens."""
        url = reverse('register')
        data = {
            'email': 'testuser@example.com',
            'full_name': 'Test User',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())

    def test_register_password_mismatch(self):
        """Test that mismatched passwords are rejected."""
        url = reverse('register')
        data = {
            'email': 'testuser@example.com',
            'full_name': 'Test User',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass456!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """Test that duplicate email registration is rejected."""
        User.objects.create_user(
            email='existing@example.com', password='Pass123!', full_name='Existing'
        )
        url = reverse('register')
        data = {
            'email': 'existing@example.com',
            'full_name': 'Duplicate User',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Test that login returns JWT tokens and user info."""
        User.objects.create_user(
            email='login@example.com', password='SecurePass123!', full_name='Login User'
        )
        url = reverse('token_obtain_pair')
        data = {'email': 'login@example.com', 'password': 'SecurePass123!'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_wrong_password(self):
        """Test that wrong password is rejected."""
        User.objects.create_user(
            email='login@example.com', password='SecurePass123!', full_name='Login User'
        )
        url = reverse('token_obtain_pair')
        data = {'email': 'login@example.com', 'password': 'WrongPassword!'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='profile@example.com', password='Pass123!', full_name='Profile User'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profile@example.com')

    def test_update_profile(self):
        url = reverse('users:profile')
        response = self.client.patch(url, {'full_name': 'Updated Name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Name')

    def test_update_location(self):
        url = reverse('users:location-update')
        data = {'latitude': 24.8607, 'longitude': 67.0011}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertAlmostEqual(float(self.user.latitude), 24.8607, places=4)

    def test_change_password(self):
        url = reverse('users:password-change')
        data = {
            'old_password': 'Pass123!',
            'new_password': 'NewSecure456!',
            'confirm_password': 'NewSecure456!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Re-login with new password
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecure456!'))

    def test_update_fcm_token(self):
        url = reverse('users:fcm-token-update')
        response = self.client.post(url, {'fcm_token': 'test-fcm-token-123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.fcm_token, 'test-fcm-token-123')


class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='reset@example.com', password='OldPass123!', full_name='Reset User'
        )

    def test_request_password_reset(self):
        url = reverse('users:password-reset-request')
        response = self.client.post(url, {'email': 'reset@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            UserVerification.objects.filter(
                user=self.user, verification_type='password_reset'
            ).exists()
        )

    def test_confirm_password_reset(self):
        # Create a verification code
        from apps.users.services import send_password_reset_email
        code = send_password_reset_email(self.user)

        url = reverse('users:password-reset-confirm')
        data = {
            'email': 'reset@example.com',
            'code': code,
            'new_password': 'BrandNew789!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('BrandNew789!'))

    def test_confirm_wrong_code(self):
        url = reverse('users:password-reset-confirm')
        data = {
            'email': 'reset@example.com',
            'code': '000000',
            'new_password': 'BrandNew789!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
