import logging
import traceback
from django.http import JsonResponse

class GlobalErrorHandlerMiddleware:
    """
    Middleware to catch and log all unhandled exceptions and return a consistent error response.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as exc:
            logging.error("Unhandled Exception: %s\n%s", exc, traceback.format_exc())
            return JsonResponse({
                "error": "Internal server error.",
                "detail": str(exc)
            }, status=500)
