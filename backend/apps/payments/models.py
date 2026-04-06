"""
Payment models for RoadAid Network.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Transaction(models.Model):
    """
    Transaction model for payments.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')
        CANCELLED = 'cancelled', _('Cancelled')
    
    class PaymentMethod(models.TextChoices):
        CARD = 'card', _('Credit/Debit Card')
        CASH = 'cash', _('Cash')
        BARTER = 'barter', _('Barter')
        WALLET = 'wallet', _('In-App Wallet')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.OneToOneField(
        'requests.ServiceRequest',
        on_delete=models.CASCADE,
        related_name='transaction'
    )
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments_made'
    )
    payee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments_received'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD
    )
    
    # Stripe fields
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_client_secret = models.CharField(max_length=200, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Promo code
    promo_code = models.ForeignKey(
        'admin_panel.PromoCode',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='transactions',
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Transaction {self.id}: {self.amount} {self.currency}"

    def mark_completed(self):
        """Mark transaction as completed."""
        from django.utils import timezone
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def mark_failed(self, error_message: str = ''):
        """Mark transaction as failed."""
        self.status = self.Status.FAILED
        if error_message:
            self.metadata['error'] = error_message
        self.save(update_fields=['status', 'metadata'])


class Wallet(models.Model):
    """
    In-app wallet for users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet for {self.user.email}: {self.balance} {self.currency}"

    def add_funds(self, amount: float):
        """Add funds to wallet."""
        from decimal import Decimal
        self.balance += Decimal(str(amount))
        self.save(update_fields=['balance'])

    def deduct_funds(self, amount: float) -> bool:
        """
        Deduct funds from wallet.
        Returns False if insufficient funds.
        """
        from decimal import Decimal
        amount = Decimal(str(amount))
        if self.balance >= amount:
            self.balance -= amount
            self.save(update_fields=['balance'])
            return True
        return False


class WalletTransaction(models.Model):
    """
    Tracks wallet top-ups and withdrawals.
    """
    
    class TransactionType(models.TextChoices):
        TOP_UP = 'top_up', _('Top Up')
        WITHDRAWAL = 'withdrawal', _('Withdrawal')
        PAYMENT = 'payment', _('Payment')
        REFUND = 'refund', _('Refund')
        EARNING = 'earning', _('Earning')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    related_transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
