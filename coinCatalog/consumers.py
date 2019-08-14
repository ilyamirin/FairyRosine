from io import BytesIO

from channels.consumer import SyncConsumer, AsyncConsumer
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from concurrent.futures import ThreadPoolExecutor
import time
import numpy as np
import base64
from asgiref.sync import async_to_sync
import json
from PIL import Image
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()


class StreamConsumer(AsyncWebsocketConsumer):
    groups = ["recognize-faces"]

    def __init__(self, *args):
        super().__init__(*args)
        print("consumer created")

    async def connect(self):
        print('connection successful!!')
        await self.accept()

    async def faces_ready(self, message):
        await self.send(json.dumps(message))
        print(f'{message}')

    async def receive(self, text_data=None, bytes_data=None):
        try:
            print(f"process {len(text_data) if text_data else 0} len bytes={len(bytes_data) if bytes_data else 0}")
            await channel_layer.send("recognizefaces", {"type": "recognize", "text_data": text_data, "bytes_data": bytes_data})
        except Exception as e:
            print(e)

    async def disconnect(self, close_code):
        print("disconnect ", close_code)
