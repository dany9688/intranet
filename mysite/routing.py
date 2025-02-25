from channels.routing import ProtocolTypeRouter, URLRouter
import mysite.routing

application = ProtocolTypeRouter({
    "websocket": URLRouter(mysite.routing.websocket_urlpatterns),
})
