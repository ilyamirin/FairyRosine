from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

import coinCatalog.consumers
from coinCatalog.consumers import StreamConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    url(r'^stream/$', StreamConsumer),
                ]
            )
        )
    ),
})
