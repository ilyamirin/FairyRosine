from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

from coinCatalog.consumers import StreamConsumer
from workers.consumers import FaceRecognitionConsumer
from workers.stt_worker import SpeechRecognitionConsumer

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
        'recognizefaces': FaceRecognitionConsumer,
        'speech_recognizer': SpeechRecognitionConsumer,
    }),
})
