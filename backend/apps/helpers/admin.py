"""
Admin configuration for Helper management.
"""
from django.contrib import admin
from .models import Helper, VehicleType, ServiceType, HelperSchedule


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'base_price', 'price_multiplier', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'estimated_duration_minutes', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


class HelperScheduleInline(admin.TabularInline):
    model = HelperSchedule
    extra = 0


@admin.register(Helper)
class HelperAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'verification_status', 'is_available', 
        'rating_avg', 'total_jobs', 'created_at'
    ]
    list_filter = ['verification_status', 'is_available', 'is_online', 'created_at']
    search_fields = ['user__email', 'user__full_name', 'license_number']
    readonly_fields = ['rating_avg', 'rating_count', 'total_jobs', 'total_earnings', 'created_at', 'updated_at']
    filter_horizontal = ['vehicle_types', 'service_types']
    inlines = [HelperScheduleInline]
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Professional Info', {'fields': ('license_number', 'bio', 'years_experience')}),
        ('Specializations', {'fields': ('vehicle_types', 'service_types')}),
        ('Availability', {'fields': ('is_available', 'is_online', 'last_online', 'service_radius_km')}),
        ('Stats', {'fields': ('rating_avg', 'rating_count', 'total_jobs', 'total_earnings')}),
        ('Verification', {'fields': ('verification_status', 'verified_at', 'id_document', 'license_document')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    actions = ['verify_helpers', 'suspend_helpers']

    @admin.action(description='Verify selected helpers')
    def verify_helpers(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            verification_status=Helper.VerificationStatus.VERIFIED,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} helper(s) verified.')

    @admin.action(description='Suspend selected helpers')
    def suspend_helpers(self, request, queryset):
        updated = queryset.update(
            verification_status=Helper.VerificationStatus.SUSPENDED,
            is_available=False
        )
        self.message_user(request, f'{updated} helper(s) suspended.')
