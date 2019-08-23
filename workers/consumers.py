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


class TimeShifter:
    def get_age(self, timestamp):
        if not hasattr(self, "shift"):
            self.set_shift(timestamp)
        return time.time() - timestamp - self.shift

    def set_shift(self, timestamp):
        now = time.time()
        self.shift = now - timestamp
        print(f"sync clock, shift = {self.shift} seconds")

    def sync_clock(self, message):
        try:
            timestamp = message["timestamp"]
            self.set_shift(timestamp)
        except Exception as e:
            print(e)


class FaceRecognitionConsumer(SyncConsumer, TimeShifter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("face worker created", flush=True)
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
            age = self.get_age(timestamp)
            print(f"face {'pass: ' if age >= 1 else 'go: '} {age}")
            if age >= 1:
                return
            start_recog = time.time()
            faces, boxes, landmarks = self.recognizer.detectFaces(img_data)
            if len(boxes) > 0:
                faces, boxes = sorted_faces(faces, boxes, 10)
                embeddings = self.recognizer._getEmbedding(faces)
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
        except Exception as e:
            print(e)

    def register(self):
        pass


class CoinRecognitionConsumer(SyncConsumer, TimeShifter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("coin worker created", flush=True)
        path = "C:/Projects/darknet_win"
        sys.path.append(path)
        import darknet
        sys.path.pop()
        self.dn = darknet

        cfg = r"C:\Projects\coins\config"
        config_path = os.path.join(cfg, "yolov3.cfg")
        meta_path = os.path.join(cfg, "coins.data")
        weight_path = os.path.join(cfg, "yolov3_best.weights")

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

        print(f"({self.dn.network_width(self.net_main)} {self.dn.network_height(self.net_main)}")
        self.darknet_image = darknet.make_image(darknet.network_width(self.net_main), darknet.network_height(self.net_main), 3)

    def recognize(self, message):
        try:
            uid = message["uid"]
            timestamp, frame_read = get_image_data_from_bytes_data(message["bytes_data"])
            age = self.get_age(timestamp)
            print(f"coin {'pass: ' if age >= 1 else 'go: '} {age}")
            if age >= 1:
                return
            start_recog = time.time()
            frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb,
                                       (self.dn.network_width(self.net_main),
                                        self.dn.network_height(self.net_main)),
                                       interpolation=cv2.INTER_LINEAR)

            self.dn.copy_image_from_bytes(self.darknet_image, frame_resized.tobytes())

            detections = self.dn.detect_image(self.net_main, self.meta_main, self.darknet_image, thresh=0.5)
            response = []
            kx = frame_rgb.shape[1] / self.dn.network_width(self.net_main)
            ky = frame_rgb.shape[0] / self.dn.network_height(self.net_main)

            for label, confidence, (x1, y1, width, height) in detections:
                label = label.decode()
                x1 = x1*kx
                y1 = y1*ky
                coords = [
                    int(y1 - height*ky/2), int(x1 - width*kx/2),
                    int(y1 + height*ky/2), int(x1 + width*kx/2)
                ]

                response_item = coords + [label] + [confidence]
                response.append(response_item)
            end_recog = time.time()
            print(f"coin recog time = {end_recog - start_recog}")
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




