"""
ASGI config for RoadAid Network project.
Configures Django Channels for WebSocket support.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roadaid.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import WebSocket URL patterns after Django is initialized
from apps.chat.routing import websocket_urlpatterns as chat_urls
from apps.requests.routing import websocket_urlpatterns as request_urls
from apps.notifications.routing import websocket_urlpatterns as notification_urls

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                chat_urls + request_urls + notification_urls
            )
        )
    ),
})
