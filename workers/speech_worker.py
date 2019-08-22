from channels.consumer import SyncConsumer, AsyncConsumer
from asgiref.sync import async_to_sync, sync_to_async

from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
import os

from channels.layers import get_channel_layer

server_channel_layer = get_channel_layer("server")


class SpeechConsumer(AsyncConsumer):
    def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        print("speech worker created", flush=True)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Projects/google-speech-auth.json"
        self.client = speech_v1.SpeechClient()
        encoding = enums.RecognitionConfig.AudioEncoding.FLAC
        sample_rate_hertz = 44100
        language_code = "ru-RU"
        self.config = {"encoding": encoding, "sample_rate_hertz": sample_rate_hertz, "language_code": language_code}

    async def recognize_speech(self, message):
        try:
            uid = message["uid"]
            audio = message["audio"]
            response = await sync_to_async(self.client.recognize)(self.config, audio)
            print(response, flush=True)
            await server_channel_layer.group_send(
                "speech",
                {
                    "type": "recognized_speech_ready",
                    "text": response,
                    "uid": uid,
                },
            )
        except Exception as e:
            print(e)
