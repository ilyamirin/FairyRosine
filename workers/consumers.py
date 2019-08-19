import os
from io import BytesIO
from time import sleep
import sys
import json
import base64
import time
import numpy as np
import sys
from scipy import misc
import copy
from PIL import Image
from channels.consumer import SyncConsumer, AsyncConsumer
from channels import routing
from asgiref.sync import async_to_sync


def area(box):
    return abs(box[2] - box[0]) * abs(box[3] - box[1])


def sorted_faces(faces, boxes, n=5):
    idxs = np.array([i for (b, i) in sorted([(area(b), i) for i, b in enumerate(boxes)], reverse=True)[:n]])
    return np.array(faces)[idxs], np.array(boxes)[idxs]


class FaceRecognitionConsumer(SyncConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("worker created", flush=True)
        print("recognizer is ready")
        self.fps_counter = 0
        self.fps_start = time.time()
        self.actual_fps = 0

    def recognize(self, message):
        try:
            text_data = json.loads(message["text_data"]) if message["text_data"] else None
            bytes_data = message["bytes_data"][13:]
            async_to_sync(self.channel_layer.group_send)(
                "recognize-faces",
                {
                    "type": "faces_ready",
                    "text": bytes_data,
                },
            )
        except Exception as e:
            print(e)

    def register(self):
        pass
