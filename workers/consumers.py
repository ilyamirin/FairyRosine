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
import cv2


server_channel_layer = get_channel_layer("server")


def area(box):
    return abs(box[2] - box[0]) * abs(box[3] - box[1])


def sorted_faces(faces, boxes, n=5):
    idxs = np.array([i for (b, i) in sorted([(area(b), i) for i, b in enumerate(boxes)], reverse=True)[:n]])
    return np.array(faces)[idxs], np.array(boxes)[idxs]


def get_image_data_from_bytes_data(bytes_data):
    image_bytes_data = bytes_data[13:]
    image_bytes_data = BytesIO(image_bytes_data)
    img = Image.open(image_bytes_data)
    img_data = np.array(img)
    timestamp = float(bytes_data[:13]) / 1000
    return timestamp, img_data


class FaceRecognitionConsumer(SyncConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("worker created", flush=True)
        sys.path.append("C:/Projects/ServantGrunbeld")

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
            uid = message["uid"]
            timestamp, img_data = get_image_data_from_bytes_data(message["bytes_data"])

            if time.time() - timestamp >= 0.5:
                print('pass frame: ' + str(time.time() - timestamp))
                return
            else:
                print('success: ' + str(time.time() - timestamp))

            start_recog = time.time()
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
                    "uid": uid,
                },
            )
            # print('BackgroundTaskConsumer.recognize waited a sec with timestamp={}'.format(msg))
        except Exception as e:
            print(e)

    def register(self):
        pass


class CoinRecognitionConsumer(SyncConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("coin worker created", flush=True)
        path = "C:/Projects/darknet_win"
        sys.path.append(path)
        import darknet
        sys.path.pop()
        self.dn = darknet

        config_path = f"{path}/yolov3.cfg"
        weight_path = f"{path}/backup/yolov3_last.weights"
        meta_path = r"C:\Projects\coins\cfg\coins.data"  # "./cfg/coco.data"

        self.net_main = darknet.load_net_custom(config_path.encode("ascii"), weight_path.encode("ascii"), 0, 1)
        self.meta_main = darknet.load_meta(meta_path.encode("ascii"))
        with open(meta_path) as metaFH:
            meta_contents = metaFH.read()
            import re
            match = re.search("names *= *(.*)$", meta_contents, re.IGNORECASE | re.MULTILINE)
            result = match.group(1) if match else None
            if os.path.exists(result):
                with open(result) as namesFH:
                    names_list = namesFH.read().strip().split("\n")
                    self.alt_names = [x.strip() for x in names_list]
        self.darknet_image = darknet.make_image(darknet.network_width(self.net_main), darknet.network_height(self.net_main), 3)

    def recognize(self, message):
        try:
            uid = message["uid"]
            timestamp, frame_read = get_image_data_from_bytes_data(message["bytes_data"])

            start_recog = time.time()
            frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb,
                                       (self.dn.network_width(self.net_main),
                                        self.dn.network_height(self.net_main)),
                                       interpolation=cv2.INTER_LINEAR)

            self.dn.copy_image_from_bytes(self.darknet_image, frame_resized.tobytes())

            detections = self.dn.detect_image(self.net_main, self.meta_main, self.darknet_image, thresh=0.5)
            response = []
            for detection in detections:
                label = detection[0].decode()
                confedence = detection[1]
                # y1 x1
                # y2 x2
                coords = [
                    int(detection[2][1]), int(detection[2][0]),
                    int(detection[2][1] + detection[2][3]), int(detection[2][0] + detection[2][2])]
                response_item = coords + [label + str(confedence)]
                response.append(response_item)
            end_recog = time.time()
            print(f"coin recog time = {end_recog - start_recog}")
            if len(response) == 0:
                return
            async_to_sync(server_channel_layer.group_send)(
                "recognize-coins",
                {
                    "type": "coins_ready",
                    "text": response,
                    "uid": uid,
                },
            )
        except Exception as e:
            print(e)




