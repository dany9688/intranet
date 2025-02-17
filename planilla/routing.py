from django.urls import re_path
from planilla import consumers

websocket_urlpatterns = [
    re_path(r"ws/location/$", consumers.LocationConsumer.as_asgi()),  # 🔥 Asegurar que Location usa `$`
    re_path(r'ws/notificaciones/(?P<destacamento>[\w-]+)/$', consumers.NotificacionConsumer.as_asgi()),

]
