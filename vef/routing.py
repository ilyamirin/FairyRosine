from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

from coinCatalog.consumers import StreamConsumer
from coinCatalog.dialog_consumer import DialogServerConsumer
from workers.consumers import FaceRecognitionConsumer, CoinRecognitionConsumer
from workers.dialog_worker import DialogConsumer
from workers.speech_worker import GoogleSpeechConsumer, YdxSpeechConsumer, AzureSpeechConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    url(r'^stream1/', StreamConsumer),
                    url(r'^dialog/', DialogServerConsumer)
                ]
            )
        )
    ),
    'channel': ChannelNameRouter({
        'recognizefaces': FaceRecognitionConsumer,
        'recognizecoins': CoinRecognitionConsumer,
        'dialog': DialogConsumer,
        'speech': YdxSpeechConsumer,
    }),
})
