import os
from io import BytesIO
from time import sleep
import sys
import json
import base64
import time
import numpy as np
import sys
import copy
from PIL import Image
from channels.consumer import SyncConsumer, AsyncConsumer
from channels import routing
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


server_channel_layer = get_channel_layer("server")


def area(box):
    return abs(box[2] - box[0]) * abs(box[3] - box[1])


def sorted_faces(faces, boxes, n=5):
    idxs = np.array([i for (b, i) in sorted([(area(b), i) for i, b in enumerate(boxes)], reverse=True)[:n]])
    return np.array(faces)[idxs], np.array(boxes)[idxs]


class FaceRecognitionConsumer(SyncConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("worker created", flush=True)
        sys.path.append("C:/Users/dvfu/Desktop/coinCatalog/git_projs/ServantGrunbeld")

        from FaceRecognition.InsightFaceRecognition import FaceRecognizer, RecognizerConfig
        from FaceDetection.RetinaFaceDetector import RetinaFace
        from FaceDetection.Config import DetectorConfig
        from DataBaseKit.DataBaseHDF import DataBase as DBHDF
        # from DataBaseKit.DjangoAPIWrapper import DataBase as DBDjango

        self.dataBase = DBHDF(
            filepath=RecognizerConfig.DATA_BASE_PATH
        )

        # os.environ["DJANGO_SETTINGS_MODULE"] = "DataBaseKit.DataBase.settings"
        # dataBase = DBDjango(password="bs420")

        sys.path.pop()

        # os.environ.setdefault("MXNET_CUDNN_AUTOTUNE_DEFAULT", "0")
        print("preparing detector")
        self.detector = RetinaFace(
            prefix=DetectorConfig.PREFIX,
            epoch=DetectorConfig.EPOCH
        )
        print("preparing recognizer")
        self.recognizer = FaceRecognizer(
            prefix=RecognizerConfig.PREFIX,
            epoch=RecognizerConfig.EPOCH,
            dataBase=self.dataBase,
            detector=self.detector
        )
        print("recognizer is ready")
        self.fps_counter = 0
        self.fps_start = time.time()
        self.actual_fps = 0

    def recognize(self, message):
        try:
            # self.fps_counter += 1
            # if time.time() - self.fps_start > 2:
            #     self.actual_fps = self.fps_counter / (time.time() - self.fps_start)
            #     self.fps_start = time.time()
            #     self.fps_counter = 0
            # print(f"FPS = {self.actual_fps}")

            # text_data = json.loads(message["text_data"]) if message["text_data"] else None
            timestamp = float(message["bytes_data"][:13]) / 1000
            bytes_data = message["bytes_data"][13:]
            if time.time() - timestamp >= 0.5:
                print('pass frame: ' + str(time.time() - timestamp))
                return
            else:
                print('success: ' + str(time.time() - timestamp))
            start_recog = time.time()
            # if not bytes_data:
            #     bytes_data = base64.b64decode(text_data["img"].split(',')[1].encode())
            bytes_data = BytesIO(bytes_data)
            img = Image.open(bytes_data)
            img_data = np.array(img)
            faces, boxes, landmarks = self.recognizer.detectFaces(img_data)
            faces, boxes = sorted_faces(faces, boxes, 10)
            embeddings = self.recognizer._getEmbedding(faces)
            # embeddings = [self.recognizer._getEmbedding(face) for face in faces]
            users = []
            for embed in embeddings:
                result, scores = self.recognizer.identify(embed)
                users.append(result)

            boxes = boxes.tolist()
            response = [b + [users[idx]] for idx, b in enumerate(boxes)]
            # response = response
            end_recog = time.time()
            print(f"recog time = {end_recog - start_recog}")
            async_to_sync(server_channel_layer.group_send)(
                "recognize-faces",
                {
                    "type": "faces_ready",
                    "text": response,
                },
            )
            # print('BackgroundTaskConsumer.recognize waited a sec with timestamp={}'.format(msg))
        except Exception as e:
            print(e)

    def register(self):
        pass


class CoinRecognitionConsumer(SyncConsumer):
    pass


# rec = FaceRecognitionConsumer(None)
