import subprocess
from blur.blur import blur_video
from ..models import AudioDetection, VideoDetection
import cv2
from typing import List
from audio_censor.sound import censor_audio
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
        sourceVideo: str,
        sourceAudio: str,
        out: str,
        videoSegments: List[VideoDetection],
        audioSegments: List[AudioDetection]):
    # sourceAudio file will be deleted after it has been read

    defult_tmp_dir = tempfile._get_default_tempdir()
    tempOutAudio = '{}/{}.wav'.format(defult_tmp_dir,
                                      next(tempfile._get_candidate_names()))
    tempOutVideo = '{}/{}.avi'.format(defult_tmp_dir,
                                      next(tempfile._get_candidate_names()))
    try:
        cap = cv2.VideoCapture(sourceVideo)

        censor_audio(sourceAudio, tempOutAudio, audioSegments)
        os.remove(sourceAudio)

        blur_video(cap, tempOutVideo, videoSegments)

        merge(tempOutVideo, tempOutAudio, out)
    except Exception as e:
        logger.error(f"Error message is {e}")
    finally:
        os.remove(tempOutAudio)
        os.remove(tempOutVideo)


if __name__ == "__main__":
    sourceVideo = "/home/vlasov/folder/pyfilter/hackathon_part_1.mp4"
    resultVideo = "/home/vlasov/folder/pyfilter/hackathon_part_1_out.mp4"

    seg1 = VideoDetection(time_start=0, time_end=3, corner_1=[
        590, 730], corner_2=[730, 570])
    seg2 = VideoDetection(time_start=0, time_end=23, corner_1=[
        1090, 630], corner_2=[1630, 170])
    seg3 = VideoDetection(time_start=20, time_end=25, corner_1=[
        1290, 730], corner_2=[1730, 370])
    tf1 = AudioDetection(time_start=0, time_end=5)
    tf2 = AudioDetection(time_start=7, time_end=10000)

    sourceAudio = "/home/vlasov/folder/pyfilter/hackathon_part_1.wav"
    extract_wav(sourceVideo, sourceAudio)
    censor(sourceVideo, sourceAudio, resultVideo,
           [seg1, seg2, seg3], [tf1, tf2])
