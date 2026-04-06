"""
Payment services for Stripe integration.
"""
import logging
from typing import Optional, Dict, Any
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger(__name__)


def get_stripe_client():
    """
    Get configured Stripe client.
    Returns None if not configured.
    """
    try:
        import stripe
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        if not stripe.api_key:
            logger.warning("Stripe API key not configured.")
            return None
        return stripe
    except ImportError:
        logger.error("Stripe library not installed.")
        return None


def create_payment_intent(
    amount: Decimal,
    currency: str = 'usd',
    customer_email: str = None,
    metadata: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a Stripe payment intent.
    
    Args:
        amount: Amount in decimal (e.g., 10.00)
        currency: Currency code (default: usd)
        customer_email: Customer's email for receipt
        metadata: Additional metadata
    
    Returns:
        Dict with payment_intent_id and client_secret, or None on failure
    """
    stripe = get_stripe_client()
    if not stripe:
        return None
    
    try:
        # Convert to cents
        amount_cents = int(amount * 100)
        
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency.lower(),
            receipt_email=customer_email,
            metadata=metadata or {},
            automatic_payment_methods={'enabled': True},
        )
        
        return {
            'payment_intent_id': intent.id,
            'client_secret': intent.client_secret,
            'status': intent.status
        }
    except Exception as e:
        logger.error(f"Failed to create payment intent: {e}")
        return None


def confirm_payment_intent(payment_intent_id: str) -> Optional[Dict[str, Any]]:
    """
    Check the status of a payment intent.
    
    Args:
        payment_intent_id: Stripe payment intent ID
    
    Returns:
        Dict with status and details, or None on failure
    """
    stripe = get_stripe_client()
    if not stripe:
        return None
    
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return {
            'status': intent.status,
            'amount': intent.amount / 100,
            'currency': intent.currency,
            'succeeded': intent.status == 'succeeded'
        }
    except Exception as e:
        logger.error(f"Failed to retrieve payment intent: {e}")
        return None


def create_refund(payment_intent_id: str, amount: Decimal = None) -> Optional[Dict[str, Any]]:
    """
    Create a refund for a payment.
    
    Args:
        payment_intent_id: Stripe payment intent ID
        amount: Amount to refund (None for full refund)
    
    Returns:
        Dict with refund details, or None on failure
    """
    stripe = get_stripe_client()
    if not stripe:
        return None
    
    try:
        params = {'payment_intent': payment_intent_id}
        if amount:
            params['amount'] = int(amount * 100)
        
        refund = stripe.Refund.create(**params)
        return {
            'refund_id': refund.id,
            'status': refund.status,
            'amount': refund.amount / 100
        }
    except Exception as e:
        logger.error(f"Failed to create refund: {e}")
        return None


def process_cash_payment(transaction) -> bool:
    """
    Process a cash payment (mark as completed).
    
    Args:
        transaction: Transaction model instance
    
    Returns:
        True if processed successfully
    """
    try:
        transaction.mark_completed()
        
        # Add to helper's wallet
        from .models import Wallet, WalletTransaction
        wallet, created = Wallet.objects.get_or_create(user=transaction.payee)
        wallet.add_funds(float(transaction.amount))
        
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type=WalletTransaction.TransactionType.EARNING,
            amount=transaction.amount,
            balance_after=wallet.balance,
            description=f"Earning from service request",
            related_transaction=transaction
        )
        
        return True
    except Exception as e:
        logger.error(f"Failed to process cash payment: {e}")
        return False


def process_wallet_payment(transaction) -> bool:
    """
    Process a wallet payment.
    
    Args:
        transaction: Transaction model instance
    
    Returns:
        True if processed successfully
    """
    try:
        from .models import Wallet, WalletTransaction
        
        # Get payer's wallet
        payer_wallet = Wallet.objects.filter(user=transaction.payer).first()
        if not payer_wallet:
            transaction.mark_failed("No wallet found for payer")
            return False
        
        # Check balance
        if not payer_wallet.deduct_funds(float(transaction.amount)):
            transaction.mark_failed("Insufficient wallet balance")
            return False
        
        # Record payer's transaction
        WalletTransaction.objects.create(
            wallet=payer_wallet,
            transaction_type=WalletTransaction.TransactionType.PAYMENT,
            amount=-transaction.amount,
            balance_after=payer_wallet.balance,
            description=f"Payment for service request",
            related_transaction=transaction
        )
        
        # Add to payee's wallet
        payee_wallet, _ = Wallet.objects.get_or_create(user=transaction.payee)
        payee_wallet.add_funds(float(transaction.amount))
        
        WalletTransaction.objects.create(
            wallet=payee_wallet,
            transaction_type=WalletTransaction.TransactionType.EARNING,
            amount=transaction.amount,
            balance_after=payee_wallet.balance,
            description=f"Earning from service request",
            related_transaction=transaction
        )
        
        transaction.mark_completed()
        return True
        
    except Exception as e:
        logger.error(f"Failed to process wallet payment: {e}")
        transaction.mark_failed(str(e))
        return False
