from io import BytesIO

from .models import AudioResult, VideoResult


def process_video(video_data: bytes) -> tuple[VideoResult, AudioResult, BytesIO]:
    pass
