from channels.consumer import SyncConsumer, AsyncConsumer
from asgiref.sync import async_to_sync, sync_to_async

from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from pydub import AudioSegment
import os
import io
import requests
import json
import sys

from channels.layers import get_channel_layer

server_channel_layer = get_channel_layer("server")


class GoogleSpeechConsumer(AsyncConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


class YdxSpeechConsumer(SyncConsumer):
    YDX_FOLDER_ID = "b1gb0dbhis374v3uqm6e"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("speech worker created", flush=True)
        self.ydx_yam_token = open("token.txt", "r").read().strip()

    def recognize_speech(self, message):
        try:
            uid = message["uid"]
            audio = AudioSegment(data=message["audio"])
            f = io.BytesIO()
            audio.export(out_f=f, format='ogg')

            params = "&".join([
                "topic=general",
                "folderId=%s" % self.YDX_FOLDER_ID,
                "lang=ru-RU"
            ])
            headers = {
                'Authorization': f'Bearer {self.ydx_yam_token}',
            }
            proxies = {'http': 'http://proxy.dvfu.ru:3128', 'https': 'http://proxy.dvfu.ru:3128'}
            response_data = requests.post(
                "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % params,
                headers=headers, data=f.getbuffer(), proxies=proxies)
            decoded_data = json.loads(response_data.text)
            print(decoded_data)
            text = decoded_data.get("result") if decoded_data.get("error_code") is None else ""
            if not decoded_data.get("error_code") is None:
                self.ydx_yam_token = open("token.txt", "r").read().strip()
            print(text, flush=True)
            async_to_sync(server_channel_layer.group_send)(
                "speech",
                {
                    "type": "recognized_speech_ready",
                    "text": text,
                    "uid": uid,
                },
            )
        except Exception as e:
            print(e)
            try:
                self.ydx_yam_token = open("token.txt", "r").read().strip()
            except Exception as e:
                print(e)


class AzureSpeechConsumer(SyncConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("creating azure speech worker...", flush=True)
        sys.path.append("C:/Projects/ServantGrunbeld")
        from SpeechRecognition.AzureRecognition import AzureRecognizer
        sys.path.pop()
        self.recognizer = AzureRecognizer()
        print("speech worker created", flush=True)

    def recognize_speech(self, message):
        try:
            uid = message["uid"]
            print(uid, flush=True)
            text = self.recognizer.processAudio(message["audio"])
            print(text)
            async_to_sync(server_channel_layer.group_send)(
                "speech",
                {
                    "type": "recognized_speech_ready",
                    "text": text,
                    "uid": uid,
                },
            )
        except Exception as e:
            print(e)
