from channels.consumer import SyncConsumer, AsyncConsumer
from asgiref.sync import async_to_sync, sync_to_async

from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from pydub import AudioSegment
import os
import io
import requests
import json

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
    YDX_IAM_TOKEN = "CggaATEVAgAAABKABCBzyP_WYpHB8usa70is_RKjknw8tEEQkIdghmeEh-4wkoRn-prFT4ohi6DGUcxQBUeh1cJzExfCWCN7Me4sIXZ-jn_CMzUGHA9jqpe4_BT9yh0po9_XIllCKKiJDsoF6bHp0TQyWqQGbXfT9WH8rDtXfehggCFNNv6CyKdSvd2Y_mAbCPOvdFs4DYg7HihDtM9fnoQuDAd1Y-NOxiHa_t1-KOvYe7gMlo5FpeibPBlGdtNUGuMqbTxSr8HEmtvRw0vadf0kFedcFI-BqRIgJWy4v-B-8cJ_wf2_PNm9t5CqEsHd6g7zPFoKr0HyMCuzXrJjAkF4_U46ueCdXQwZ22RGakvMabmDr3-L3UcCnkY7V8-cRnrOGu8TippIMoQnD_EfNk09OhBUR8mLVW4htHeqioLCNkFNni-lhE3giExaVzyH6ZzIOiVV-9Pzz1va9QlfALlgjx7W8o-Dnighj4HP2I07Guadh70HkVwv-lDLDADGlRzmHnIajT7pU8UPnndFBjBrFMgYIzQ5iml29zrqvlIfGK1wIv51mg4-3FFs8sUaYvhP35xzM8O_SonUbB1hp1fi10zGIpO6mAMBrjLIsbotkFUhGkmk9r7Jwaz8m-ImBSiLsRvcT1H1VSzui-Fzik2sW_2cp3erTshncakAeCsDCU04yDy42CRlUqnRGmMKIDJiZWJmMmY2ZWUyODQ1Mjg5NzY0YWU0YTc3MTNmYTAyEJ3H-uoFGN2Y_eoFIiEKFGFqZWIwdGtlZWo1bmlzcWk2N2dyEglhbGV4aXNraGJaADACOAFKCBoBMRUCAAAAUAEg8gQ"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("speech worker created", flush=True)

    def recognize_speech(self, message):
        # try:
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
                'Authorization': f'Bearer {self.YDX_IAM_TOKEN}',
            }
            proxies = {'http': 'http://proxy.dvfu.ru:3128', 'https': 'http://proxy.dvfu.ru:3128'}
            response_data = requests.post(
                "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % params,
                headers=headers, data=f.getbuffer(), proxies=proxies)
            decoded_data = json.loads(response_data.text)
            print(decoded_data)
            text = decoded_data.get("result") if decoded_data.get("error_code") is None else ""
            print(text, flush=True)
            async_to_sync(server_channel_layer.group_send)(
                "speech",
                {
                    "type": "recognized_speech_ready",
                    "text": text,
                    "uid": uid,
                },
            )
        # except Exception as e:
        #     print(e)


def test():
    import subprocess
    with open(os.devnull, 'rb') as devnull:
        pass
        # p = subprocess.Popen("ls", stdin=devnull, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # f = io.BytesIO()
    # print(isinstance(f, os.PathLike))



# if __name__ == "__main__":
#     test()