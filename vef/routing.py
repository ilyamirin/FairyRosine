from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

import coinCatalog.consumers
from coinCatalog.consumers import StreamConsumer
from workers.consumers import FaceRecognitionConsumer

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
    'channel': ChannelNameRouter({
        # Messages directed to the `recognizefaces` channel will be passed to our consumer
        'recognizefaces': FaceRecognitionConsumer,
    }),
})
