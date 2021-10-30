from pydantic import BaseModel


class TaskMessage(BaseModel):
    source: str
    prefix: str


class Task(BaseModel):
    task_id: int
    message: TaskMessage


class AudioDetection(BaseModel):
    time_start: float
    time_end: float


class AudioResult(BaseModel):
    result: list[AudioDetection]


class VideoDetection(BaseModel):
    time_start: float
    time_end: float
    corner_1: tuple[int, int]
    corner_2: tuple[int, int]


class VideoResult(BaseModel):
    result: list[VideoDetection]
