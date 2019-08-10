from io import BytesIO

from channels.consumer import SyncConsumer, AsyncConsumer
from concurrent.futures import ThreadPoolExecutor
import time
import base64
import numpy as np
import sys
from json import loads
from scipy import misc
import copy
from PIL import Image
import json


sys.path.append("/home/anothername/projects/ServantGrunbeld")
from FaceRecognition.InsightFaceRecognition import FaceRecognizer, RecognizerConfig
from FaceDetection.RetinaFaceDetector import RetinaFace
from FaceDetection.Config import DetectorConfig
from DataBase.DataBaseHDF import DataBase
sys.path.pop()

dataBase = DataBase(
    filepath="./FaceRecognitionData/Temp/users_face_exp.hdf"
)

print("preparing detector")
detector = RetinaFace(
    prefix=DetectorConfig.PREFIX,
    epoch=DetectorConfig.EPOCH
)
print("preparing recognizer")
recognizer = FaceRecognizer(
    prefix=RecognizerConfig.PREFIX,
    epoch=RecognizerConfig.EPOCH,
    dataBase=dataBase,
    detector=detector
)
print("warming up")
# warmUp = np.zeros(shape=(480, 640, 3), dtype=np.float32)
# faces, boxes, landmarks = recognizer.detectFaces(warmUp)
# embeddings = [recognizer._getEmbedding(face) for face in faces]
# users = []
# for embed in embeddings:
#     result, scores = recognizer.identify(embed)


class StreamConsumer(AsyncConsumer):
    def __init__(self, *args):
        super().__init__(*args)
        print("consumer created")

    async def websocket_connect(self, event):
        print('connection successful!!', event)
        await self.send({
            "type": "websocket.accept",
        })

        await self.send({
            "type": "websocket.send",
            "text": "hello, world!",
        })

    async def websocket_receive(self, event):
        try:
            print("process")

            event = json.loads(event["text"])
            timestamp = float(event['timestamp']) / 1000

            assert time.time() - timestamp < 1 / 2, 'pass frame - ' + str(time.time() - timestamp)

            img_data = base64.b64decode(event["img"].split(',')[1].encode())
            img = Image.open(BytesIO(img_data))
            img_data = np.array(img)
            faces, boxes, landmarks = recognizer.detectFaces(img_data)
            embeddings = [recognizer._getEmbedding(face) for face in faces]
            users = []
            for embed in embeddings:
                result, scores = recognizer.identify(embed)
                users.append(result)
            print(f"{users}")
        except Exception as e:
            print(e)

    async def websocket_disconnect(self, event):
        print("disconnect ", event)

