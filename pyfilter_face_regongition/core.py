#!/usr/bin/env python3
# coding --utf-8--

from loguru import logger
from pathlib import Path
import face_recognition
import numpy as np
import glob
import os


# Todo: Доделать класс для создания VideoResult
class DetectFaces:
    def __init__(self, data_dir: str = os.getcwd() + "/.data/"):

        Path(data_dir).mkdir(parents=True, exist_ok=True)

        self.data_dir = data_dir
        logger.info("Detector loaded successfully")

    def __call__(self, input_image: np.ndarray, *args, **kwargs):
        result_array = list()

        logger.info("Starting face detection")

        celebs = [face_recognition.face_encodings(
            celeb)[0] for celeb in glob.glob(self.data_dir + "*.jpg")]

        face_locations = face_recognition.face_locations(input_image)
        face_encodings = face_recognition.face_encodings(
            input_image, face_locations)

        for face_encoding in face_encodings:
            result = face_recognition.compare_faces(celebs, face_encoding)

            indices = [i for i, x in enumerate(result) if x]
            logger.info(f"Found {indices} celeb faces")
            for index in indices:
                result_array.append(face_locations[index])

        return result_array


if __name__ == "__main__":
    known_image = face_recognition.load_image_file("biden.jpg")
    unknown_image = face_recognition.load_image_file("unknown.jpg")

    biden_encoding = face_recognition.face_encodings(known_image)[0]
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

    results = face_recognition.compare_faces(
        [biden_encoding], unknown_encoding)
    # the Result of [False, ...]
