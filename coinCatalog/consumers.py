from io import BytesIO

from channels.consumer import SyncConsumer, AsyncConsumer
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from concurrent.futures import ThreadPoolExecutor
import time
import numpy as np
import base64
from asgiref.sync import async_to_sync
import json
import asyncio
from PIL import Image
from channels.layers import get_channel_layer
from string import ascii_letters
import random


face_channel_layer = get_channel_layer("face")


class StreamConsumer(AsyncWebsocketConsumer):
    groups = ["recognize-faces"]

    def __init__(self, *args):
        super().__init__(*args)
        self.uid = "".join(random.choice(ascii_letters) for _ in range(8))
        print("consumer created")

    async def connect(self):
        print('connection successful!!')
        await self.accept()

    async def faces_ready(self, message):
        if message["uid"] == self.uid:
            print(f'{self.uid}: faces ready')
            await self.send(json.dumps(message))

    async def receive(self, text_data=None, bytes_data=None):
        try:
            print(f"{self.uid}: receive {len(text_data) if text_data else 0} text data, {len(bytes_data) if bytes_data else 0} bytes data")
            await asyncio.gather(
                face_channel_layer.send("recognizefaces", {"type": "recognize", "bytes_data": bytes_data, "uid": self.uid}),
            )
        except Exception as e:
            print(e)

    async def disconnect(self, close_code):
        print("disconnect ", close_code)
