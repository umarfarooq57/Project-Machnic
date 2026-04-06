"""
Payment views.
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from .models import Transaction, Wallet, WalletTransaction
from .serializers import (
    TransactionSerializer,
    CreatePaymentIntentSerializer,
    WalletSerializer,
    WalletTransactionSerializer,
    TopUpWalletSerializer,
)
from . import services


@extend_schema(tags=['Payments'])
class CreatePaymentIntentView(APIView):
    """
    Create a payment intent for a completed service request.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreatePaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from apps.requests.models import ServiceRequest
        request_id = serializer.validated_data['request_id']
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Validate request
        if service_request.user != request.user:
            return Response(
                {'error': 'You can only pay for your own requests.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if service_request.status != ServiceRequest.Status.COMPLETED:
            return Response(
                {'error': 'Can only pay for completed requests.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already paid
        if hasattr(service_request, 'transaction') and service_request.transaction.status == Transaction.Status.COMPLETED:
            return Response(
                {'error': 'This request has already been paid for.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        amount = service_request.final_price or service_request.estimated_price
        if not amount:
            return Response(
                {'error': 'No price set for this request.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_method = serializer.validated_data['payment_method']
        
        # Create transaction record
        transaction, created = Transaction.objects.get_or_create(
            request=service_request,
            defaults={
                'payer': request.user,
                'payee': service_request.helper.user,
                'amount': amount,
                'payment_method': payment_method
            }
        )
        
        if payment_method == Transaction.PaymentMethod.CARD:
            # Create Stripe payment intent
            result = services.create_payment_intent(
                amount=amount,
                customer_email=request.user.email,
                metadata={
                    'request_id': str(service_request.id),
                    'transaction_id': str(transaction.id)
                }
            )
            
            if not result:
                return Response(
                    {'error': 'Failed to create payment intent.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            transaction.stripe_payment_intent_id = result['payment_intent_id']
            transaction.stripe_client_secret = result['client_secret']
            transaction.status = Transaction.Status.PROCESSING
            transaction.save()
            
            return Response({
                'transaction': TransactionSerializer(transaction).data,
                'client_secret': result['client_secret']
            })
        
        elif payment_method == Transaction.PaymentMethod.WALLET:
            # Process wallet payment immediately
            success = services.process_wallet_payment(transaction)
            
            if not success:
                return Response(
                    {'error': 'Wallet payment failed. Check your balance.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                'transaction': TransactionSerializer(transaction).data,
                'message': 'Payment completed successfully.'
            })


@extend_schema(tags=['Payments'])
class ConfirmPaymentView(APIView):
    """
    Confirm a card payment after client-side completion.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, transaction_id):
        transaction = get_object_or_404(
            Transaction, 
            id=transaction_id,
            payer=request.user
        )
        
        if transaction.status == Transaction.Status.COMPLETED:
            return Response({'message': 'Payment already confirmed.'})
        
        if not transaction.stripe_payment_intent_id:
            return Response(
                {'error': 'No payment intent found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check payment status with Stripe
        result = services.confirm_payment_intent(transaction.stripe_payment_intent_id)
        
        if result and result['succeeded']:
            transaction.mark_completed()
            
            # Add to helper's wallet
            from .models import Wallet, WalletTransaction
            wallet, _ = Wallet.objects.get_or_create(user=transaction.payee)
            wallet.add_funds(float(transaction.amount))
            
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type=WalletTransaction.TransactionType.EARNING,
                amount=transaction.amount,
                balance_after=wallet.balance,
                description=f"Earning from service request",
                related_transaction=transaction
            )
            
            return Response({
                'message': 'Payment confirmed.',
                'transaction': TransactionSerializer(transaction).data
            })
        
        return Response(
            {'error': 'Payment not yet completed.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['Payments'])
class MarkCashPaymentView(APIView):
    """
    Mark a payment as cash (helper confirms receipt).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        from apps.requests.models import ServiceRequest
        from apps.users.permissions import IsHelper
        
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Only the assigned helper can mark as cash payment
        if not service_request.helper or service_request.helper.user != request.user:
            return Response(
                {'error': 'Only the assigned helper can confirm cash payment.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        amount = service_request.final_price or service_request.estimated_price
        if not amount:
            return Response(
                {'error': 'No price set for this request.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or update transaction
        transaction, created = Transaction.objects.get_or_create(
            request=service_request,
            defaults={
                'payer': service_request.user,
                'payee': request.user,
                'amount': amount,
                'payment_method': Transaction.PaymentMethod.CASH
            }
        )
        
        if not created:
            transaction.payment_method = Transaction.PaymentMethod.CASH
            transaction.save()
        
        services.process_cash_payment(transaction)
        
        return Response({
            'message': 'Cash payment recorded.',
            'transaction': TransactionSerializer(transaction).data
        })


@extend_schema(tags=['Payments'])
class TransactionHistoryView(generics.ListAPIView):
    """
    List transaction history for the current user.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.db.models import Q
        return Transaction.objects.filter(
            Q(payer=self.request.user) | Q(payee=self.request.user)
        )


@extend_schema(tags=['Wallet'])
class WalletView(generics.RetrieveAPIView):
    """
    Get the current user's wallet.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


@extend_schema(tags=['Wallet'])
class WalletTransactionsView(generics.ListAPIView):
    """
    List wallet transaction history.
    """
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        wallet = Wallet.objects.filter(user=self.request.user).first()
        if wallet:
            return wallet.transactions.all()
        return WalletTransaction.objects.none()


@extend_schema(tags=['Wallet'])
class TopUpWalletView(APIView):
    """
    Initiate a wallet top-up.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TopUpWalletSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        
        # Create Stripe payment intent for top-up
        result = services.create_payment_intent(
            amount=amount,
            customer_email=request.user.email,
            metadata={
                'type': 'wallet_topup',
                'user_id': str(request.user.id)
            }
        )
        
        if not result:
            return Response(
                {'error': 'Failed to create payment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'client_secret': result['client_secret'],
            'amount': float(amount)
        })
