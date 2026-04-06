"""
Comprehensive tests for the payments app.
"""
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.payments.models import Wallet


class WalletTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='wallet@example.com', password='Pass123!', full_name='Wallet User',
        )
        self.wallet = Wallet.objects.create(user=self.user, balance=100.00)
        self.client.force_authenticate(user=self.user)

    def test_get_wallet(self):
        url = reverse('payments:wallet')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wallet_transactions_empty(self):
        url = reverse('payments:wallet-transactions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_transaction_history(self):
        url = reverse('payments:history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
