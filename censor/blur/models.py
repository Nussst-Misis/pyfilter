from pydantic import BaseModel
from typing import List


class AudioDetection(BaseModel):
    time_start: float
    time_end: float


class VideoDetection(BaseModel):
    time_start: float
    time_end: float
    corner_1: List[int]
    corner_2: List[int]


class VideoResult(BaseModel):
    result: List[VideoDetection]


class AudioResult(BaseModel):
    result: List[AudioDetection]


class RecognitionResult(BaseModel):
    audio: AudioResult
    video: VideoResult
    result_file: bytes
