"""
Custom permissions for RoadAid Network.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj == request.user or (hasattr(obj, 'user') and obj.user == request.user)


class IsHelper(permissions.BasePermission):
    """
    Permission to only allow helpers to access the view.
    """
    message = 'You must be a registered helper to perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            hasattr(request.user, 'helper_profile') and 
            request.user.helper_profile is not None
        )


class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow admin users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsVerifiedUser(permissions.BasePermission):
    """
    Permission to only allow verified users.
    """
    message = 'Please verify your email/phone to perform this action.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified


class IsRequestParticipant(permissions.BasePermission):
    """
    Permission to only allow users who are part of a service request.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Check if user is the requester
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Check if user is the helper
        if hasattr(obj, 'helper') and obj.helper and obj.helper.user == request.user:
            return True
        
        return False
