"""
Admin configuration for Service Request management.
"""
from django.contrib import admin
from .models import ServiceRequest, RequestImage, RequestStatusHistory


class RequestImageInline(admin.TabularInline):
    model = RequestImage
    extra = 0
    readonly_fields = ['uploaded_at']


class RequestStatusHistoryInline(admin.TabularInline):
    model = RequestStatusHistory
    extra = 0
    readonly_fields = ['status', 'changed_by', 'notes', 'created_at']
    can_delete = False


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'helper', 'vehicle_type', 'status', 
        'urgency', 'created_at', 'completed_at'
    ]
    list_filter = ['status', 'urgency', 'vehicle_type', 'is_barter', 'created_at']
    search_fields = ['user__email', 'user__full_name', 'helper__user__email', 'issue_description']
    readonly_fields = ['created_at', 'updated_at', 'accepted_at', 'arrived_at', 'started_at', 'completed_at']
    inlines = [RequestImageInline, RequestStatusHistoryInline]
    
    fieldsets = (
        ('Users', {'fields': ('user', 'helper')}),
        ('Request Details', {'fields': (
            'vehicle_type', 'service_types', 'issue_description', 'urgency', 'status'
        )}),
        ('Location', {'fields': (
            'user_latitude', 'user_longitude', 'user_address',
            'helper_latitude', 'helper_longitude'
        )}),
        ('Timing', {'fields': (
            'eta_minutes', 'accepted_at', 'arrived_at', 'started_at', 'completed_at'
        )}),
        ('Pricing', {'fields': (
            'estimated_price', 'final_price', 'is_barter', 'barter_terms'
        )}),
        ('Cancellation', {'fields': (
            'cancelled_by', 'cancellation_reason', 'cancelled_at'
        )}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    filter_horizontal = ['service_types']
