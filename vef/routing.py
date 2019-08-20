from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

from coinCatalog.consumers import StreamConsumer
# from workers.stt_worker import SpeechRecognitionConsumer
from workers.consumers import FaceRecognitionConsumer, CoinRecognitionConsumer

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
        # 'speech_recognizer': SpeechRecognitionConsumer,
        'recognizecoins': CoinRecognitionConsumer,
    }),
})
