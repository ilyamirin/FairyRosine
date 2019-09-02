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
from string import ascii_letters
import random
from collections import defaultdict

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
    def get_age(self, timestamp, uid=None):
        if not hasattr(self, "shift"):
            self.set_shift(timestamp, uid)
        return time.time() - timestamp + self.shift

    def set_shift(self, timestamp, uid=None):
        now = time.time()
        self.shift = now - timestamp
        print(f"{uid or '?'} sync clock, shift = {self.shift} seconds")

    def sync_clock(self, message):
        try:
            timestamp = message["timestamp"]
            self.set_shift(timestamp, message["uid"])
        except Exception as e:
            print(e)


class SqliteDialoguser:
    UNKNOWN = "Unknown"

    def __init__(self):
        self.type = "sqlite3"
        self.dialog_uids = set(user.uid for user in DialogUser.objects.all())
        self.cached_vectors = {}

    def __iter__(self):
        """итерация for возвращает dialog_uid"""
        return iter(copy.deepcopy(self.dialog_uids))

    def get(self, dialog_uid):
        """Возвращает embed вектор юзера"""
        if dialog_uid not in self.cached_vectors:
            self.cached_vectors[dialog_uid] = np.frombuffer(DialogUser.objects.get(uid=dialog_uid).vector, dtype=np.float32)
        return self.cached_vectors[dialog_uid]

    def checkOutgoingName(self, dialog_uid):
        if dialog_uid == self.UNKNOWN:
            return dialog_uid
        self.add_dialog_uid(dialog_uid)
        return dialog_uid

    @staticmethod
    def randomString(length=10, pool=ascii_letters):
        return "".join(random.choice(pool) for _ in range(length))

    def _get_all_uids(self):
        return self.dialog_uids

    def recache_all_uids(self):
        self.dialog_uids = set(user.uid for user in DialogUser.objects.all())

    def add_dialog_uid(self, dialog_uid):
        self.dialog_uids.add(dialog_uid)



class FaceRecognitionConsumer(SyncConsumer, TimeShifter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("creating face worker...", flush=True)

        sys.path.append(SERVANT_DIR)

        from FaceRecognition.InsightFaceRecognition import FaceRecognizer, RecognizerConfig
        from FaceDetection.RetinaFaceDetector import RetinaFace
        from FaceDetection.Config import DetectorConfig

        self.dataBase = SqliteDialoguser()

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
        self.language = {}
        self.last_filtered = 0
        print("face worker created", flush=True)

    def filter_users(self):
        try:
            DialogUser.objects.filter(name="").delete()
        except:
            pass
        print("users filtered", flush=True)

    def recognize(self, message):
        try:
            if time.time() - self.last_filtered > 5*60:
                self.filter_users()
                self.last_filtered = time.time()
            uid = message["uid"]
            timestamp, img_data = get_image_data_from_bytes_data(message["bytes_data"])
            age = self.get_age(timestamp, uid)
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
                    # Самое большое лицо
                    if i == 0:
                        # Если мы его не знаем
                        if result == SqliteDialoguser.UNKNOWN:
                            result = SqliteDialoguser.randomString()
                            print(f"Это новый персонаж: {result}")
                            cv2.imwrite(f"photo_{result.replace('/', ' ')}.png", photo_slice)
                            user = DialogUser(
                                uid=result,
                                time_enrolled=datetime.now(),
                                photo=photo_slice.tobytes(),
                                name="",
                                vector=embed.tobytes(),
                            )
                            user.save()
                            self.dataBase.add_dialog_uid(result)
                        current_user_uid = result or None
                    display_name = DialogUser.objects.get(uid=result).name if result != SqliteDialoguser.UNKNOWN else ""
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

            display_name = DialogUser.objects.get(uid=current_user_uid).name if current_user_uid else ""
            async_to_sync(server_channel_layer.group_send)(
                "dialog-recognize-faces",
                {
                    "type": "dialog_faces_ready",
                    "uid": uid,
                    "dialog_uid": current_user_uid,
                    "dialog_photo": photo_slice_b64,
                    "display_name": display_name
                },
            )
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            self.dataBase.recache_all_uids()
            print("uids recached", flush=True)
            print(e)

    def register(self):
        pass

    def set_language(self, message):
        try:
            lang = message["lang"]
            uid = message["uid"]
            self.language[uid] = lang
        except Exception as e:
            print(e)


from coinCatalog.models import Coin, CoinDescription, ImgCoin
from vef.settings import BASE_DIR
import html

class Darknet:
    def __init__(self):
        if 'darknet' not in sys.modules:
            path = "C:/Projects/darknet_win"
            sys.path.append(path)
            import darknet
            sys.path.pop()
        self.dn = darknet

        cfg = r"C:\Projects\coins\config\47"
        config_path = os.path.join(cfg, "yolov3.cfg")
        meta_path = os.path.join(cfg, "coins.data")
        weight_path = os.path.join(cfg, "yolov3_14000.weights")

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
        self.darknet_image = darknet.make_image(darknet.network_width(self.net_main), darknet.network_height(self.net_main),                                3)
        self.category_to_id = json.loads(open(os.path.join(BASE_DIR, "category_tO_id.json"), "r").read())


dnn = None


class CoinRecognitionConsumer(SyncConsumer, TimeShifter):
    def __init__(self, *args, **kwargs):
        global dnn
        super().__init__(*args, **kwargs)
        print("coin worker created", flush=True)

        if not dnn:
            dnn = Darknet()

        self.dn = dnn.dn
        self.net_main = dnn.net_main
        self.meta_main = dnn.meta_main
        self.alt_names = dnn.alt_names
        self.darknet_image = dnn.darknet_image
        self.category_to_id = dnn.category_to_id
        self.ids = list(self.category_to_id.values())
        self.language = defaultdict(lambda: "en")
        self.response_min_cnt = 4
        self.featured_coins = random.sample(self.ids, 5*self.response_min_cnt)
        self.featured_last_updated = time.time()

    def extend_by_featured(self, response, uid):
        if time.time() - self.featured_last_updated >= 10:
            self.featured_coins = self.featured_coins[1:] + [random.choice(self.ids)]
            self.featured_last_updated = time.time()
        current_featured = -1
        while len(set(coin["id"] for coin in response)) < self.response_min_cnt:
            current_featured += 1
            coin = Coin.objects.get(catalog_id=self.featured_coins[current_featured])
            if coin.id in [coin["id"] for coin in response]:
                continue
            description = CoinDescription.objects.get(coin_id=coin, lang=self.language[uid])
            href_img = ImgCoin.objects.filter(coin_id=coin).values()[0]['href']
            coin_info = {
                "coords": [10000]*4,
                "id": coin.id,
                "confidence": 0,
                "href": href_img,
                "short_name": description.short_name,
                "featured": True,
            }
            response.append(coin_info)

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

            print(*(d[0].decode() for d in detections))
            for i, detection in enumerate(detections):
                detections[i] = (self.category_to_id[detections[i][0].decode()], *detections[i][1:])

            for label, confidence, (x1, y1, width, height) in detections:
                x1 = x1*kx
                y1 = y1*ky

                coords = [
                    int(y1 - height*ky/2), int(x1 - width*kx/2),
                    int(y1 + height*ky/2), int(x1 + width*kx/2)
                ]

                #print(f"y: {coords[0]}\tx:  {coords[1]}\th: {coords[2] - coords[0]}\tw: {coords[3] - coords[1]}")

                coin = Coin.objects.get(catalog_id=label)
                description = CoinDescription.objects.get(coin_id=coin, lang=self.language[uid])
                href_img = ImgCoin.objects.filter(coin_id=coin).values()[0]['href']
                coin_info = {
                    "coords": coords,
                    "id": coin.id,
                    "confidence": confidence,
                    "href": href_img,
                    "short_name": description.short_name,
                    "featured": False,
                }
                response.append(coin_info)

            self.extend_by_featured(response, uid)

            end_recog = time.time()
            print(f"coin recog time = {end_recog - start_recog:.3f}")
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

    def set_language(self, message):
        try:
            lang = message["lang"]
            uid = message["uid"]
            self.language[uid] = lang
        except Exception as e:
            print(e)



