#!/usr/bin/env python3
# coding --utf-8--

from loguru import logger
from pathlib import Path
from annoy import AnnoyIndex
import face_recognition
import numpy as np

THRESHOLD_DISTANCE = 0.5


# Todo: Доделать класс для создания VideoResult
class DetectFaces:
    def __init__(self, data_dir: Path = Path() / ".data"):
        Path(data_dir).mkdir(parents=True, exist_ok=True)

        self.data_dir = data_dir
        self.model = AnnoyIndex(128, "euclidean")
        self.model.load(data_dir / "faces.ann")
        logger.info("Detector loaded successfully")

    def __call__(self, input_image: np.ndarray, *args, **kwargs):
        logger.info("Starting face detection")
        result = []

        face_locations = face_recognition.face_locations(input_image)
        face_encodings = face_recognition.face_encodings(
            input_image, face_locations
        )

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            _, (distance,) = self.model.get_nns_by_vector(face_encoding, 1, include_distances=True)
            if distance > THRESHOLD_DISTANCE:
                continue
            result.append(((right, top), (left, bottom)))

        return result


if __name__ == "__main__":
    known_image = face_recognition.load_image_file("biden.jpg")
    unknown_image = face_recognition.load_image_file("unknown.jpg")

    biden_encoding = face_recognition.face_encodings(known_image)[0]
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

    results = face_recognition.compare_faces(
        [biden_encoding], unknown_encoding)
    # the Result of [False, ...]
