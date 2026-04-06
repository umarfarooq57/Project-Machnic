"""
Custom exception classes for RoadAid Network.
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class ServiceUnavailable(APIException):
    """Exception for when a service is temporarily unavailable."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable, please try again later.'
    default_code = 'service_unavailable'


class PaymentError(APIException):
    """Exception for payment processing errors."""
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Payment processing failed.'
    default_code = 'payment_error'


class LocationNotFound(APIException):
    """Exception when location services fail."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Unable to determine location.'
    default_code = 'location_not_found'


class NoHelpersAvailable(APIException):
    """Exception when no helpers are available nearby."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'No helpers available in your area at this time.'
    default_code = 'no_helpers_available'


class RequestAlreadyAccepted(APIException):
    """Exception when trying to accept an already accepted request."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'This request has already been accepted by another helper.'
    default_code = 'request_already_accepted'


class InvalidRequestStatus(APIException):
    """Exception for invalid request status transitions."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Cannot perform this action with current request status.'
    default_code = 'invalid_request_status'
