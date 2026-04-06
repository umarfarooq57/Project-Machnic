"""
Admin configuration for User management.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserVerification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model.
    """
    list_display = ['email', 'full_name', 'role', 'is_verified', 'is_active', 'created_at']
    list_filter = ['role', 'is_verified', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'full_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'phone', 'profile_image')}),
        (_('Location'), {'fields': ('latitude', 'longitude', 'last_location_update')}),
        (_('Status'), {'fields': ('role', 'is_verified', 'is_active')}),
        (_('Notifications'), {'fields': ('fcm_token',)}),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_location_update']


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    """
    Admin for UserVerification model.
    """
    list_display = ['user', 'verification_type', 'is_used', 'expires_at', 'created_at']
    list_filter = ['verification_type', 'is_used', 'created_at']
    search_fields = ['user__email', 'code']
    readonly_fields = ['created_at']
