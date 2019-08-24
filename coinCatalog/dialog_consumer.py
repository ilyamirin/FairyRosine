from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json
from channels.layers import get_channel_layer
from string import ascii_letters
import random

dialog_channel_layer = get_channel_layer("dialog")
speech_channel_layer = get_channel_layer("speech")
face_channel_layer = get_channel_layer("face")


def is_image(bytes_data):
    pref = bytes_data[:100]
    for suff in b'PNG', b'JPG', b'JPEG', b'JFIF', b'JPE':
        if suff in pref:
            return True
    return False


class DialogServerConsumer(AsyncWebsocketConsumer):
    groups = ["dialog", "speech", "recognize-faces"]

    def __init__(self, *args):
        super().__init__(*args)
        self.uid = "".join(random.choice(ascii_letters) for _ in range(8))

    async def connect(self):
        await self.accept()

    async def dialog_answer_ready(self, message):
        if message["uid"] == self.uid:
            print(f'{self.uid}: dialog ready')
            await self.send(json.dumps(message))

    async def send_to_bot(self, text):
        try:
            await dialog_channel_layer.send("dialog", {"type": "dialog_answer", "text": text, "uid": self.uid})
        except Exception as e:
            print(f"send to bot: {e}")

    async def recognized_speech_ready(self, message):
        if message["uid"] == self.uid and message["text"] != "":
            await self.send(json.dumps(message))
            await self.send_to_bot(message["text"])

    async def faces_ready(self, message):
        if message["uid"] == self.uid:
            await self.send(json.dumps(message))

    async def receive(self, text_data=None, bytes_data=None):
        try:
            print(f"{self.uid}: receive {len(text_data) if text_data else 0} text data, {len(bytes_data) if bytes_data else 0} bytes data")
            if text_data and len(text_data) > 0:
                await self.send_to_bot(text_data)
            if bytes_data and len(bytes_data) > 0:
                if is_image(bytes_data):
                    await face_channel_layer.send("recognizefaces",
                                                  {"type": "recognize", "bytes_data": bytes_data, "uid": self.uid, "dialog": True})
                else:
                    await speech_channel_layer.send("speech",
                                                    {"type": "recognize_speech", "audio": bytes_data, "uid": self.uid})
        except Exception as e:
            print(e)

    async def disconnect(self, close_code):
        print("disconnect ", close_code)
