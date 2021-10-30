from io import BytesIO

from .models import AudioResult, VideoResult


def process_video(video_data: bytes) -> tuple[VideoResult, AudioResult, BytesIO]:
    return VideoResult(result=[]), AudioResult(result=[]), BytesIO(b"123")
