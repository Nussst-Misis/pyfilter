import subprocess
from .blur.blur import blur_video
from ..models import AudioDetection, VideoDetection
import cv2
from typing import List
from .audio_censor.sound import censor_audio
import os
import tempfile
from loguru import logger


def extract_wav(video: str, out: str):
    command = "yes|ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(
        video, out)
    subprocess.call(command, shell=True)


def merge(video: str, audio: str, out: str):
    command = "yes|ffmpeg -i {} -i {} -vcodec copy {}".format(
        video, audio, out)
    subprocess.call(command, shell=True)


def censor(
        source_video: str,
        source_audio: str,
        out: str,
        viceo_segments: List[VideoDetection],
        audio_segments: List[AudioDetection]):
    # sourceAudio file will be deleted after it has been read

    temp_out_audio = os.path.join(tempfile.mkdtemp(), 'tempOut.wav')
    temp_out_video = os.path.join(tempfile.mkdtemp(), 'tempOut.avi')
    try:
        cap = cv2.VideoCapture(source_video)

        censor_audio(source_audio, temp_out_audio, audio_segments)
        os.remove(source_audio)

        blur_video(cap, temp_out_video, viceo_segments)

        merge(temp_out_video, temp_out_audio, out)
    except Exception as e:
        logger.error(f"Error message is {e}")
    finally:
        os.remove(temp_out_audio)
        os.remove(temp_out_video)


if __name__ == "__main__":
    source_video = "/home/vlasov/folder/pyfilter/hackathon_part_1.mp4"
    result_video = "/home/vlasov/folder/pyfilter/hackathon_part_1_out.mp4"

    seg1 = VideoDetection(time_start=0, time_end=3, corner_1=[
        590, 730], corner_2=[730, 570])
    seg2 = VideoDetection(time_start=0, time_end=23, corner_1=[
        1090, 630], corner_2=[1630, 170])
    seg3 = VideoDetection(time_start=20, time_end=25, corner_1=[
        1290, 730], corner_2=[1730, 370])
    tf1 = AudioDetection(time_start=0, time_end=5)
    tf2 = AudioDetection(time_start=7, time_end=10000)

    source_audio = "/home/vlasov/folder/pyfilter/hackathon_part_1.wav"
    extract_wav(source_video, source_audio)
    censor(source_video, source_audio, result_video,
           [seg1, seg2, seg3], [tf1, tf2])
