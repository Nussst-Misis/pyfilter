from io import BytesIO
from typing import Tuple
from censor.censor import censor, extract_wav
from .models import VideoDetection
import tempfile
import os

from .models import AudioResult, VideoResult
from .pyfilter_audio.audio_core import AudioProcess

# Init AudioProcessing
ap = AudioProcess()


def process_video(
        video_data: bytes) -> Tuple[VideoResult, AudioResult, BytesIO]:
    src_path = os.path.join(tempfile.mkdtemp(), 'source.mp4')
    with open(src_path, 'w') as source:
        source.write(video_data)

    out_path = os.path.join(tempfile.mkdtemp(), 'out.mp4')
    try:
        # get videoSegments in nn
        seg1 = VideoDetection(time_start=0, time_end=3, corner_1=[
            590, 730], corner_2=[730, 570])
        seg2 = VideoDetection(time_start=0, time_end=23, corner_1=[
            1090, 630], corner_2=[1630, 170])
        seg3 = VideoDetection(time_start=20, time_end=25, corner_1=[
            1290, 730], corner_2=[1730, 370])
        video_result = [seg1, seg2, seg3]
        # get audio segments from nn
        audio_result = ap(src_path)
        src_wav_path = src_path[:-3]+"wav"

        censor(src_path,
               src_wav_path,
               out_path,
               video_result, audio_result)
    finally:
        os.remove(src_path)
    out_bytes = os.read(out_path)
    return video_result, audio_result, out_bytes
