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


class FaceRecognitionConsumer(SyncConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("worker created", flush=True)
        sys.path.append("/home/anothername/projects/ServantGrunbeld")
        from FaceRecognition.InsightFaceRecognition import FaceRecognizer, RecognizerConfig
        from FaceDetection.RetinaFaceDetector import RetinaFace
        from FaceDetection.Config import DetectorConfig
        from DataBase.DataBaseHDF import DataBase
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
        # warmUp = np.zeros(shape=(480, 640, 3), dtype=np.float32)
        # faces, boxes, landmarks = recognizer.detectFaces(warmUp)
        # embeddings = [recognizer._getEmbedding(face) for face in faces]
        # users = []
        # for embed in embeddings:
        #     result, scores = recognizer.identify(embed)

    def recognize(self, text_data):
        try:
            event_text = json.loads(text_data["text_data"])
            timestamp = float(event_text['timestamp']) / 1000
            if time.time() - timestamp >= 1 / 2:
                print('pass frame - ' + str(time.time() - timestamp))
                return
            img_data = base64.b64decode(event_text["img"].split(',')[1].encode())
            img = Image.open(BytesIO(img_data))
            img_data = np.array(img)
            faces, boxes, landmarks = self.recognizer.detectFaces(img_data)
            embeddings = [self.recognizer._getEmbedding(face) for face in faces]
            users = []
            for embed in embeddings:
                result, scores = self.recognizer.identify(embed)
                users.append(result)
            # print(f"{users}: {timestamp}")

            boxes = boxes.tolist()
            response = [b + [users[idx]] for idx, b in enumerate(boxes)]
            response = json.dumps(response)

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
