"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from django.urls import re_path
from planilla import consumers
from planilla.routing import websocket_urlpatterns  # 🔥 IMPORTA ESTO

# from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket": AuthMiddlewareStack(
    #     URLRouter([
    #         re_path("ws/location/", consumers.LocationConsumer.as_asgi()), # WebSocket de geolocalización
    #         re_path("ws/notificaciones/(?P<destacamento>\w+)/$", consumers.NotificacionConsumer.as_asgi()),  # WebSocket de notificaciones
    #     ])
    # ),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)  # 🔥 IMPORTA LAS RUTAS DESDE `routing.py`
    ),
})