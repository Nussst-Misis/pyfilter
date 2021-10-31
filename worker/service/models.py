from pydantic import BaseModel
from typing import List


class TaskMessage(BaseModel):
    source: str
    prefix: str


class Task(BaseModel):
    task_id: str
    message: TaskMessage


class AudioDetection(BaseModel):
    time_start: float
    time_end: float


class AudioResult(BaseModel):
    result: List[AudioDetection]


class VideoDetection(BaseModel):
    time_start: float
    time_end: float
    corner_1: List[int]
    corner_2: List[int]


class VideoResult(BaseModel):
    result: List[VideoDetection]
