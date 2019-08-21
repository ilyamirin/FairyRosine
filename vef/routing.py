from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

from coinCatalog.consumers import StreamConsumer
# from workers.stt_worker import SpeechRecognitionConsumer
from workers.consumers import FaceRecognitionConsumer, CoinRecognitionConsumer
from workers.dialog_worker import DialogConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    url(r'^stream1/', StreamConsumer),
                    url(r'^dialog/', StreamConsumer)
                ]
            )
        )
    ),
    'channel': ChannelNameRouter({
        'recognizefaces': FaceRecognitionConsumer,
        # 'speech_recognizer': SpeechRecognitionConsumer,
        'recognizecoins': CoinRecognitionConsumer,
        'dialog': DialogConsumer,
    }),
})
