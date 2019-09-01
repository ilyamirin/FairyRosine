import os
import django
import json
import html
import sys
import datetime
import cv2

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vef.settings")
django.setup()

from vef.settings import BASE_DIR, SERVANT_DIR
from coinCatalog.models import DialogUser
from workers.consumers import SqliteDialoguser


sys.path.append(SERVANT_DIR)
from FaceRecognition.InsightFaceRecognition import FaceRecognizer, RecognizerConfig
from FaceDetection.RetinaFaceDetector import RetinaFace
from FaceDetection.Config import DetectorConfig
sys.path.pop()
dataBase = SqliteDialoguser()
detector = RetinaFace(
    prefix=DetectorConfig.PREFIX,
    epoch=DetectorConfig.EPOCH
)
recognizer = FaceRecognizer(
    prefix=RecognizerConfig.PREFIX,
    epoch=RecognizerConfig.EPOCH,
    dataBase=dataBase,
    detector=detector
)


def enroll_person(user: DialogUser, cv2_images: list):
    for i, img_data in enumerate(cv2_images):
        if img_data is None:
            print(f"{user.name}: skip photo #{i} (image is null)")
            continue
        faces, boxes, landmarks = recognizer.detectFaces(img_data)
        if len(faces) != 1:
            print(f"{user.name}: skip photo #{i} (too many faces)")
            continue
        embed = recognizer._getEmbedding(faces)[0]
        user.vector = embed.tobytes()
        user.uid = SqliteDialoguser.randomString()
        user.save()
        print(f"{user.name}: photo #{i} enrolled")


def filenames_to_cv2images(*filenames):
    return [cv2.imread(os.path.join(BASE_DIR, filename)) for filename in filenames]


now = datetime.datetime.now()
users_to_add = [
    # (
    #     DialogUser(
    #         name="Владимир Путин",
    #         time_enrolled=now,
    #     ), filenames_to_cv2images(
    #         "faces/putin1.jpg",
    #         "faces/putin2.jpg",
    #         "faces/putin3.jpg",
    #         "faces/putin4.jpg",
    #     )
    # ),
    # (
    #     DialogUser(
    #         name="Герман Греф",
    #         time_enrolled=now,
    #     ), filenames_to_cv2images(
    #         "faces/gref1.jpg",
    #         "faces/gref2.jpg",
    #         "faces/gref3.jpg",
    #         "faces/gref4.jpg",
    #     )
    # ),
    # (
    #     DialogUser(
    #         name="Нарендра Моди",
    #         time_enrolled=now,
    #     ), filenames_to_cv2images(
    #         "faces/modi1.jpg",
    #         "faces/modi2.jpg",
    #         "faces/modi3.jpg",
    #         "faces/modi4.jpg",
    #     )
    # ),
]

for user in users_to_add:
    enroll_person(*user)
