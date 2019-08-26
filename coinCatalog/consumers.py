from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json
import asyncio
from channels.layers import get_channel_layer
from string import ascii_letters
import random
import operator
import time
import copy

face_channel_layer = get_channel_layer("face")
coin_channel_layer = get_channel_layer("coin")
clock_channel_layer = get_channel_layer("clock")


class StreamConsumer(AsyncWebsocketConsumer):
    groups = ["recognize-faces", "recognize-coins"]

    def __init__(self, *args):
        super().__init__(*args)
        self.uid = "".join(random.choice(ascii_letters) for _ in range(8))
        self.rec_coins = {}
        self.cnt_rec_coins = 0
        print("consumer created", flush=True)

    async def sync_clock(self):
        while True:
            message = {"type": "sync_clock", "timestamp": time.time(), "uid": self.uid}
            try:
                await asyncio.gather(
                    clock_channel_layer.send("recognizefaces", message),
                    clock_channel_layer.send("recognizecoins", message),
                    self.send(json.dumps(message)),
                )
                print("sync clock", flush=True)
            except Exception as e:
                print('sync clock exception: ' + str(e))
            await asyncio.sleep(4)

    async def connect(self):
        print('connection successful!!')
        await self.accept()
        asyncio.get_event_loop().create_task(self.sync_clock())

    async def faces_ready(self, message):
        if message["uid"] == self.uid:
            res = copy.deepcopy(message)
            res['type'] = 'face'
            await self.send(json.dumps(res))

    async def coins_ready(self, message):
        if message["uid"] == self.uid:
            res = copy.deepcopy(message)
            res['type'] = 'coin'
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

            await self.send(json.dumps(res))

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
