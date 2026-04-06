"""
WebSocket URL routing for requests app.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/requests/(?P<request_id>[0-9a-f-]+)/$', 
            consumers.RequestConsumer.as_asgi()),
    re_path(r'ws/requests/$', 
            consumers.RequestConsumer.as_asgi()),
    re_path(r'ws/helper/requests/$', 
            consumers.HelperRequestsConsumer.as_asgi()),
]
