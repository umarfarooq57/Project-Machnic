"""
Payment serializers.
"""
from rest_framework import serializers
from .models import Transaction, Wallet, WalletTransaction


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for transactions.
    """
    payer_name = serializers.CharField(source='payer.full_name', read_only=True)
    payee_name = serializers.CharField(source='payee.full_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'request', 'payer', 'payer_name', 'payee', 'payee_name',
            'amount', 'currency', 'status', 'payment_method',
            'stripe_client_secret', 'description',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'stripe_client_secret', 'created_at', 'completed_at'
        ]


class CreatePaymentIntentSerializer(serializers.Serializer):
    """
    Serializer for creating a payment intent.
    """
    request_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(
        choices=[Transaction.PaymentMethod.CARD, Transaction.PaymentMethod.WALLET],
        default=Transaction.PaymentMethod.CARD
    )


class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for wallet.
    """
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'currency', 'updated_at']
        read_only_fields = ['id', 'balance', 'updated_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for wallet transactions.
    """
    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'transaction_type', 'amount', 'balance_after',
            'description', 'created_at'
        ]


class TopUpWalletSerializer(serializers.Serializer):
    """
    Serializer for wallet top-up.
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1)
