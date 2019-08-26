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
from coinCatalog.models import DialogUser
from datetime import datetime
import base64
from vef.settings import SERVANT_DIR


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
        return time.time() - timestamp + self.shift

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
        print("creating face worker...", flush=True)

        sys.path.append(SERVANT_DIR)

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
        print("preparing detector...")
        self.detector = RetinaFace(
            prefix=DetectorConfig.PREFIX,
            epoch=DetectorConfig.EPOCH
        )
        print("detector is ready")
        print("preparing recognizer...")
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
        print("face worker created", flush=True)

    def recognize(self, message):
        try:
            known_prefix = "Known"
            uid = message["uid"]
            timestamp, img_data = get_image_data_from_bytes_data(message["bytes_data"])
            age = self.get_age(timestamp)
            print(f"face {'pass: ' if age >= 1 else 'go: '} {age}")
            if age >= 1:
                return
            start_recog = time.time()
            faces, boxes, landmarks = self.recognizer.detectFaces(img_data)
            current_user_uid, photo_slice, photo_slice_b64 = [None]*3
            if len(boxes) > 0:
                # y1 x1 y2 x2
                faces, boxes = sorted_faces(faces, boxes, 10)
                embeddings = self.recognizer._getEmbedding(faces)
                y1, x1, y2, x2 = boxes[0]
                w, h, div, (maxy, maxx, *_) = x2 - x1, y2 - y1, 5, img_data.shape
                photo_slice = img_data[
                    max(y1 - h//div, 0):min(y2 + h//div, maxy - 1),
                    max(x1 - w//div, 0):min(x2 + w//div, maxx - 1)
                ]
                users = []
                for i, embed in enumerate(embeddings):
                    result, scores = self.recognizer.identify(embed)
                    display_name = ""
                    # Самое большое лицо
                    if i == 0:
                        # Если мы его не знаем
                        if result == "Unknown":
                            result = self.recognizer.dataBase.checkIncomingName(known_prefix, addIndex=True)
                            print(f"Это новый персонаж: {result}")
                            self.recognizer.enroll(embed, result)
                            cv2.imwrite(f"{result.replace('/', ' ')}.png", photo_slice)
                            user = DialogUser(uid=result, time_enrolled=datetime.now(), photo=photo_slice.tobytes(), name="")
                            user.save()
                        current_user_uid = result
                    try:
                        display_name = DialogUser.objects.get(uid=result).name
                    except:
                        pass
                    users.append(display_name)
            boxes = boxes.tolist()
            response = [b + [users[idx]] for idx, b in enumerate(boxes)]
            if photo_slice is not None:
                photo_slice_b64 = cv2.cvtColor(photo_slice, cv2.COLOR_BGR2RGB)
                photo_slice_b64 = base64.b64encode(cv2.imencode('.png', photo_slice_b64)[1]).decode()
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

            name = ""
            if current_user_uid is not None:
                try:
                    name = DialogUser.objects.get(uid=current_user_uid).name
                except:
                    name = current_user_uid if not current_user_uid.startswith(known_prefix) else ""
                    user = DialogUser(uid=current_user_uid, time_enrolled=datetime.now(), photo=photo_slice.tobytes(), name=name)
                    user.save()
            async_to_sync(server_channel_layer.group_send)(
                "dialog-recognize-faces",
                {
                    "type": "dialog_faces_ready",
                    "uid": uid,
                    "dialog_uid": current_user_uid,
                    "dialog_photo": photo_slice_b64,
                    "display_name": name
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
            frame_rgb = frame_read
            # frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb,
                                       (self.dn.network_width(self.net_main),
                                        self.dn.network_height(self.net_main)),
                                       interpolation=cv2.INTER_LINEAR)

            print((self.dn.network_width(self.net_main),
                                        self.dn.network_height(self.net_main)))

            self.dn.copy_image_from_bytes(self.darknet_image, frame_resized.tobytes())

            detections = self.dn.detect_image(self.net_main, self.meta_main, self.darknet_image, thresh=0.3)
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




