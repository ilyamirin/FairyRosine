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
        sys.path.append("/home/anothername/projects/ServantGrunbeld")
        from FaceRecognition.InsightFaceRecognition import FaceRecognizer, RecognizerConfig
        from FaceDetection.RetinaFaceDetector import RetinaFace
        from FaceDetection.Config import DetectorConfig
        from DataBaseKit.DataBaseHDF import DataBase
        sys.path.pop()

        self.dataBase = DataBase(
            filepath="./FaceRecognitionData/Temp/users_face_exp.hdf"
        )

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
            self.fps_counter += 1
            if time.time() - self.fps_start > 2:
                self.actual_fps = self.fps_counter / (time.time() - self.fps_start)
                self.fps_start = time.time()
                self.fps_counter = 0
            print(f"FPS = {self.actual_fps}")
            text_data = json.loads(message["text_data"]) if message["text_data"] else None
            bytes_data = message["bytes_data"]
            if text_data:
                timestamp = float(text_data['timestamp']) / 1000
                if time.time() - timestamp >= 1 / 2:
                    print('pass frame: ' + str(time.time() - timestamp))
                    return
                else:
                    print('success: ' + str(time.time() - timestamp))
            start_recog = time.time()
            if not bytes_data:
                bytes_data = base64.b64decode(text_data["img"].split(',')[1].encode())
            bytes_data = BytesIO(bytes_data)
            img = Image.open(bytes_data)
            img_data = np.array(img)
            faces, boxes, landmarks = self.recognizer.detectFaces(img_data)
            faces, boxes = sorted_faces(faces, boxes, 5)
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
            async_to_sync(self.channel_layer.group_send)(
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
