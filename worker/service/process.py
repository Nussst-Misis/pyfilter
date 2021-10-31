from io import BytesIO
from typing import Tuple
from censor.censor import censor, extract_wav
from .models import VideoDetection, AudioDetection
import tempfile
import os

from .models import AudioResult, VideoResult
from pyfilter_audio.audio_core import AudioProcess

# Init AudioProcessing
ap = AudioProcess()


def process_video(
        video_data: bytes) -> Tuple[VideoResult, AudioResult, BytesIO]:
    srcPath = os.path.join(tempfile.mkdtemp(), 'source.mp4')
    with open(srcPath, 'w') as source:
        source.write(video_data)

    srcWavPath = os.path.join(tempfile.mkdtemp(), 'source.wav')
    outPath = os.path.join(tempfile.mkdtemp(), 'out.mp4')
    try:
        # extract wav in nn
        # wrcWavPath will be deleted in censor
        extract_wav(srcPath, srcWavPath)
        # get videoSegments in nn
        seg1 = VideoDetection(time_start=0, time_end=3, corner_1=[
            590, 730], corner_2=[730, 570])
        seg2 = VideoDetection(time_start=0, time_end=23, corner_1=[
            1090, 630], corner_2=[1630, 170])
        seg3 = VideoDetection(time_start=20, time_end=25, corner_1=[
            1290, 730], corner_2=[1730, 370])
        videoResult = [seg1, seg2, seg3]
        # get audio segments from nn
        audioResult = ap(srcPath)

        censor(srcPath,
               srcWavPath,
               outPath,
               videoResult, audioResult)
    finally:
        os.remove(srcPath)
    outBytes = os.read(outPath)
    return videoResult, audioResult, outBytes
