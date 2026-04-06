"""
Admin Panel serializers.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.helpers.models import Helper
from .models import PromoCode, Dispute, PlatformConfig, EmergencyContact

User = get_user_model()


class DashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_helpers = serializers.IntegerField()
    verified_helpers = serializers.IntegerField()
    pending_helpers = serializers.IntegerField()
    active_requests = serializers.IntegerField()
    completed_requests = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    today_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    open_disputes = serializers.IntegerField()


class AdminUserSerializer(serializers.ModelSerializer):
    is_helper = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone', 'role',
            'is_verified', 'is_active', 'is_helper',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']


class AdminHelperSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Helper
        fields = [
            'id', 'user_email', 'user_name', 'shop_name',
            'experience_years', 'verification_status',
            'rating_avg', 'total_jobs', 'total_earnings',
            'is_available', 'is_online', 'created_at',
        ]
        read_only_fields = ['id', 'rating_avg', 'total_jobs', 'total_earnings', 'created_at']


class HelperVerificationSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject', 'suspend'])
    reason = serializers.CharField(required=False, allow_blank=True)


class PromoCodeSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = PromoCode
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'min_order_amount', 'max_discount_amount', 'usage_limit',
            'times_used', 'valid_from', 'valid_until', 'is_active', 'is_valid',
            'created_at',
        ]
        read_only_fields = ['id', 'times_used', 'created_at']


class PromoCodeApplySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=30)
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class DisputeSerializer(serializers.ModelSerializer):
    raised_by_email = serializers.EmailField(source='raised_by.email', read_only=True)
    resolved_by_email = serializers.EmailField(source='resolved_by.email', read_only=True, default=None)

    class Meta:
        model = Dispute
        fields = [
            'id', 'request', 'raised_by', 'raised_by_email',
            'description', 'status', 'resolution_notes',
            'resolved_by', 'resolved_by_email', 'resolved_at',
            'created_at',
        ]
        read_only_fields = ['id', 'raised_by', 'resolved_by', 'resolved_at', 'created_at']


class DisputeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ['request', 'description']


class DisputeResolveSerializer(serializers.Serializer):
    resolution_notes = serializers.CharField()


class PlatformConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformConfig
        fields = ['key', 'value', 'description', 'updated_at']
        read_only_fields = ['updated_at']


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ['id', 'name', 'phone', 'relationship', 'created_at']
        read_only_fields = ['id', 'created_at']


class RevenueReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()
