"""
Admin Panel views for RoadAid Network.
Dashboard analytics, user / helper management, promo codes, disputes.
"""
from decimal import Decimal
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.users.permissions import IsAdminUser
from apps.helpers.models import Helper
from apps.requests.models import ServiceRequest
from apps.payments.models import Transaction
from .models import PromoCode, Dispute, PlatformConfig, EmergencyContact
from .serializers import (
    DashboardStatsSerializer,
    AdminUserSerializer,
    AdminHelperSerializer,
    HelperVerificationSerializer,
    PromoCodeSerializer,
    PromoCodeApplySerializer,
    DisputeSerializer,
    DisputeCreateSerializer,
    DisputeResolveSerializer,
    PlatformConfigSerializer,
    EmergencyContactSerializer,
    RevenueReportSerializer,
)

User = get_user_model()


# ──────────────────────────────────────────────
#  Dashboard
# ──────────────────────────────────────────────

@extend_schema(tags=['Admin'])
class DashboardStatsView(APIView):
    """Aggregated platform-wide statistics for the admin dashboard."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        stats = {
            'total_users': User.objects.filter(is_active=True).count(),
            'total_helpers': Helper.objects.count(),
            'verified_helpers': Helper.objects.filter(
                verification_status=Helper.VerificationStatus.VERIFIED
            ).count(),
            'pending_helpers': Helper.objects.filter(
                verification_status=Helper.VerificationStatus.PENDING
            ).count(),
            'active_requests': ServiceRequest.objects.filter(
                status__in=[
                    ServiceRequest.Status.PENDING,
                    ServiceRequest.Status.SEARCHING,
                    ServiceRequest.Status.MATCHED,
                    ServiceRequest.Status.ACCEPTED,
                    ServiceRequest.Status.EN_ROUTE,
                    ServiceRequest.Status.ARRIVED,
                    ServiceRequest.Status.IN_PROGRESS,
                ]
            ).count(),
            'completed_requests': ServiceRequest.objects.filter(
                status=ServiceRequest.Status.COMPLETED
            ).count(),
            'total_revenue': Transaction.objects.filter(
                status=Transaction.Status.COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0'),
            'today_revenue': Transaction.objects.filter(
                status=Transaction.Status.COMPLETED,
                completed_at__date=today,
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0'),
            'open_disputes': Dispute.objects.filter(status=Dispute.Status.OPEN).count(),
        }
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)


@extend_schema(tags=['Admin'])
class RevenueReportView(APIView):
    """Daily revenue report for a date range."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timezone.timedelta(days=days)

        report = (
            Transaction.objects
            .filter(status=Transaction.Status.COMPLETED, completed_at__gte=start_date)
            .annotate(date=TruncDate('completed_at'))
            .values('date')
            .annotate(revenue=Sum('amount'), transaction_count=Count('id'))
            .order_by('date')
        )
        serializer = RevenueReportSerializer(report, many=True)
        return Response(serializer.data)


# ──────────────────────────────────────────────
#  User Management
# ──────────────────────────────────────────────

@extend_schema(tags=['Admin'])
class AdminUserListView(generics.ListAPIView):
    """List all users with optional search and filtering."""
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        qs = User.objects.all()
        search = self.request.query_params.get('search', '')
        role = self.request.query_params.get('role', '')
        is_active = self.request.query_params.get('is_active', '')

        if search:
            qs = qs.filter(
                Q(email__icontains=search) |
                Q(full_name__icontains=search) |
                Q(phone__icontains=search)
            )
        if role:
            qs = qs.filter(role=role)
        if is_active in ('true', 'false'):
            qs = qs.filter(is_active=is_active == 'true')
        return qs


@extend_schema(tags=['Admin'])
class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    """Get or update a specific user (admin can toggle is_active, role, etc.)."""
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = User.objects.all()


# ──────────────────────────────────────────────
#  Helper Verification
# ──────────────────────────────────────────────

@extend_schema(tags=['Admin'])
class AdminHelperListView(generics.ListAPIView):
    """List all helpers with optional status filter."""
    serializer_class = AdminHelperSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        qs = Helper.objects.select_related('user').all()
        vs = self.request.query_params.get('verification_status', '')
        if vs:
            qs = qs.filter(verification_status=vs)
        return qs


@extend_schema(tags=['Admin'])
class AdminHelperVerifyView(APIView):
    """Approve, reject, or suspend a helper."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        serializer = HelperVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            helper = Helper.objects.get(pk=pk)
        except Helper.DoesNotExist:
            return Response({'error': 'Helper not found.'}, status=status.HTTP_404_NOT_FOUND)

        action = serializer.validated_data['action']
        status_map = {
            'approve': Helper.VerificationStatus.VERIFIED,
            'reject': Helper.VerificationStatus.REJECTED,
            'suspend': Helper.VerificationStatus.SUSPENDED,
        }

        helper.verification_status = status_map[action]
        helper.save(update_fields=['verification_status'])

        # Update user role on approval
        if action == 'approve':
            helper.user.role = 'helper'
            helper.user.save(update_fields=['role'])

        return Response({
            'message': f'Helper {action}d successfully.',
            'verification_status': helper.verification_status,
        })


# ──────────────────────────────────────────────
#  Promo Codes
# ──────────────────────────────────────────────

@extend_schema(tags=['Admin'])
class PromoCodeListCreateView(generics.ListCreateAPIView):
    """List or create promo codes (admin only)."""
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


@extend_schema(tags=['Admin'])
class PromoCodeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a promo code."""
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


@extend_schema(tags=['Payments'])
class ApplyPromoCodeView(APIView):
    """
    Public endpoint for users to validate and preview a promo code discount.
    Does NOT consume the code — that happens at payment time.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PromoCodeApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code_str = serializer.validated_data['code'].upper().strip()
        order_amount = serializer.validated_data['order_amount']

        try:
            promo = PromoCode.objects.get(code=code_str)
        except PromoCode.DoesNotExist:
            return Response({'error': 'Invalid promo code.'}, status=status.HTTP_404_NOT_FOUND)

        if not promo.is_valid:
            return Response({'error': 'This promo code is expired or fully used.'}, status=status.HTTP_400_BAD_REQUEST)

        discount = promo.calculate_discount(order_amount)
        return Response({
            'code': promo.code,
            'discount_type': promo.discount_type,
            'discount_amount': str(discount),
            'final_amount': str(Decimal(str(order_amount)) - discount),
        })


# ──────────────────────────────────────────────
#  Disputes
# ──────────────────────────────────────────────

@extend_schema(tags=['Admin'])
class DisputeListView(generics.ListAPIView):
    """List disputes — admin sees all, normal users see their own."""
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Dispute.objects.select_related('raised_by', 'resolved_by').all()
        return Dispute.objects.filter(raised_by=user)


@extend_schema(tags=['Disputes'])
class DisputeCreateView(generics.CreateAPIView):
    """Create a new dispute for a service request."""
    serializer_class = DisputeCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(raised_by=self.request.user)


@extend_schema(tags=['Admin'])
class DisputeResolveView(APIView):
    """Resolve an open dispute (admin only)."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        serializer = DisputeResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            dispute = Dispute.objects.get(pk=pk)
        except Dispute.DoesNotExist:
            return Response({'error': 'Dispute not found.'}, status=status.HTTP_404_NOT_FOUND)

        if dispute.status in (Dispute.Status.RESOLVED, Dispute.Status.CLOSED):
            return Response({'error': 'Dispute is already resolved.'}, status=status.HTTP_400_BAD_REQUEST)

        dispute.resolve(
            admin_user=request.user,
            notes=serializer.validated_data['resolution_notes'],
        )
        return Response({
            'message': 'Dispute resolved.',
            'dispute': DisputeSerializer(dispute).data,
        })


# ──────────────────────────────────────────────
#  Platform Config
# ──────────────────────────────────────────────

@extend_schema(tags=['Admin'])
class PlatformConfigListView(generics.ListCreateAPIView):
    queryset = PlatformConfig.objects.all()
    serializer_class = PlatformConfigSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


@extend_schema(tags=['Admin'])
class PlatformConfigDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlatformConfig.objects.all()
    serializer_class = PlatformConfigSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


# ──────────────────────────────────────────────
#  Emergency Contacts (User-facing)
# ──────────────────────────────────────────────

@extend_schema(tags=['Safety'])
class EmergencyContactListCreateView(generics.ListCreateAPIView):
    """List or create emergency contacts for the authenticated user."""
    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EmergencyContact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['Safety'])
class EmergencyContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete an emergency contact."""
    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EmergencyContact.objects.filter(user=self.request.user)
