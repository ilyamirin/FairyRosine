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
import operator


face_channel_layer = get_channel_layer("face")
coin_channel_layer = get_channel_layer("coin")


class StreamConsumer(AsyncWebsocketConsumer):
    groups = ["recognize-faces", "recognize-coins"]

    def __init__(self, *args):
        super().__init__(*args)
        self.uid = "".join(random.choice(ascii_letters) for _ in range(8))
        self.rec_coins = {}
        self.cnt_rec_coins = 0
        print("consumer created")

    async def connect(self):
        print('connection successful!!')
        await self.accept()

    async def faces_ready(self, message):
        if message["uid"] == self.uid:
            message['type'] = 'face'
            print(f'{self.uid}: faces ready')
            await self.send(json.dumps(message))

    async def coins_ready(self, message):
        if message["uid"] == self.uid:
            message['type'] = 'coin'
            print(f'{self.uid}: coins ready')

            for coin in message["text"]:
                self.cnt_rec_coins += 1
                self.rec_coins[coin[4]] = 1 + self.rec_coins.get(coin[4], 0)

            if self.cnt_rec_coins >= 20:
                coins = [(key, value) for key, value in self.rec_coins.items()]
                coins = list(reversed(sorted(coins, key=operator.itemgetter(1))))
                resp = {
                    "type": "recognized_coins",
                    "text": coins
                }
                await self.send(json.dumps(resp))
                self.cnt_rec_coins = 0
                self.rec_coins = {}

            await self.send(json.dumps(message))

    async def receive(self, text_data=None, bytes_data=None):
        try:
            print(f"{self.uid}: receive {len(text_data) if text_data else 0} text data, {len(bytes_data) if bytes_data else 0} bytes data")
            await asyncio.gather(
                face_channel_layer.send("recognizefaces",
                                        {"type": "recognize", "bytes_data": bytes_data, "uid": self.uid}),
                coin_channel_layer.send("recognizecoins",
                                        {"type": "recognize", "bytes_data": bytes_data, "uid": self.uid}),
            )
        except Exception as e:
            print(e)

    async def disconnect(self, close_code):
        print("disconnect ", close_code)
