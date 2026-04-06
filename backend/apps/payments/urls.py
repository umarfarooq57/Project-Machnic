"""
URL configuration for payments app.
"""
from django.urls import path
from .views import (
    CreatePaymentIntentView,
    ConfirmPaymentView,
    MarkCashPaymentView,
    TransactionHistoryView,
    WalletView,
    WalletTransactionsView,
    TopUpWalletView,
)

app_name = 'payments'

urlpatterns = [
    # Payments
    path('create/', CreatePaymentIntentView.as_view(), name='create-intent'),
    path('confirm/<uuid:transaction_id>/', ConfirmPaymentView.as_view(), name='confirm'),
    path('cash/<uuid:request_id>/', MarkCashPaymentView.as_view(), name='mark-cash'),
    path('history/', TransactionHistoryView.as_view(), name='history'),
    
    # Wallet
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('wallet/transactions/', WalletTransactionsView.as_view(), name='wallet-transactions'),
    path('wallet/topup/', TopUpWalletView.as_view(), name='wallet-topup'),
]
