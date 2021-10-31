from io import BytesIO
from typing import Tuple
from .censor.censor import censor, extract_wav
from .models import VideoDetection
import tempfile
import os
import cv2

from .models import AudioResult, VideoResult
from .audio.audio_core import AudioProcess
from .video import DetectFaces

# Init AudioProcessing
audio_processor = AudioProcess()
face_detector = DetectFaces()


def process_video(video_data: bytes) -> Tuple[VideoResult, AudioResult, BytesIO]:
    src_path = os.path.join(tempfile.mkdtemp(), "source.mp4")
    with open(src_path, "wb") as source:
        source.write(video_data)

    out_path = os.path.join(tempfile.mkdtemp(), "out.mp4")
    try:
        # get videoSegments in nn
        video_result = face_detector.detect_faces(src_path)
        # get audio segments from nn
        audio_result = audio_processor(src_path)
        src_wav_path = src_path[:-3] + "wav"

        censor(src_path, src_wav_path, out_path, video_result, audio_result)
    finally:
        os.remove(src_path)
    with open(out_path, "wb") as f:
        result = BytesIO(f.read())

    return VideoResult(result=video_result), AudioResult(result=audio_result), result
