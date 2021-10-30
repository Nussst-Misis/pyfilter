import types

from pydantic import BaseModel
from io import BytesIO


class AudioDetection(BaseModel):
    time_start: float
    time_end: float


class VideoDetection(BaseModel):
    time_start: float
    time_end: float
    corner_1: tuple[int, int]
    corner_2: tuple[int, int]


class AudioResult(BaseModel):
    result: list[AudioDetection]

