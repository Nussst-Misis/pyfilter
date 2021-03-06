import cv2
from typing import List
from pydantic import BaseModel
import numpy as np
from ...models import VideoDetection


class TimeframeSegments(BaseModel):
    time_start: np.float64
    time_end: np.float64
    segments: List[List[int]]


def simple_blur(image: np.ndarray, factor=3.0) -> np.ndarray:
    # automatically determine the size of the blurring kernel based
    # on the spatial dimensions of the input image
    (h, w) = image.shape[:2]
    kW = int(w / factor)
    kH = int(h / factor)
    # ensure the width of the kernel is odd
    if kW % 2 == 0:
        kW -= 1
    # ensure the height of the kernel is odd
    if kH % 2 == 0:
        kH -= 1
    # apply a Gaussian blur to the input image using our computed
    # kernel size
    return cv2.GaussianBlur(image, (kW, kH), 0)


def crop_video_detection_to_fit(segment: List[int], img: np.ndarray):
    for point in segment:
        if point[0] < 0:
            point[0] = 0
        if point[0] >= img.shape[1]:
            point[0] = img.shape[1] - 1
        if point[1] < 0:
            point[1] = 0
        if point[1] >= img.shape[0]:
            point[1] = img.shape[0] - 1


def blur_image_video_detection(img: np.ndarray, segments: List[List[int]]):
    for seg in segments:
        crop_video_detection_to_fit(seg, img)
        roi = img[seg[1][1] : seg[0][1], seg[0][0] : seg[1][0]]
        if roi.shape[0] == 0 or roi.shape[1] == 0:
            continue
        blurred = simple_blur(roi)
        img[seg[1][1] : seg[0][1], seg[0][0] : seg[1][0]] = blurred


def merge_video_detections(segments: List[VideoDetection]) -> List[TimeframeSegments]:
    timeline = np.zeros(len(segments) * 2)
    for i in range(len(segments)):
        timeline[i * 2] = segments[i].time_start
        timeline[i * 2 + 1] = segments[i].time_end
    timeline = sorted(timeline)
    timeline = list(dict.fromkeys(timeline))

    res = []
    for i in range(len(timeline) - 1):
        t1 = timeline[i]
        t2 = timeline[i + 1]
        segs = TimeframeSegments(time_start=t1, time_end=t2, segments=[])
        for seg in segments:
            if seg.time_start <= t1 and seg.time_end >= t2:
                segs.segments.append([seg.corner_1, seg.corner_2])
        if len(segs.segments) != 0:
            res.append(segs)
    return res


def transfer_n_frames(cap, out, n: int, modify_function=None):
    for i in range(n):
        ret, frame = cap.read()

        if ret:
            if modify_function is not None:
                modify_function(frame)
            out.write(frame)
        else:
            print("unexpected EOF")
            raise


def blur_from_timeframes(cap, timeframes: List[TimeframeSegments], out):
    # consecutive timeframes containint one or more segments
    fps = cap.get(cv2.CAP_PROP_FPS)
    cur = 0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for timeframe in timeframes:
        print("blurring segments: ", timeframe)
        mod_start = min(0, int(fps * (timeframe.time_start)))
        mod_end = min(total, int(fps * (timeframe.time_end)))

        if mod_start - cur > 0:
            transfer_n_frames(cap, out, mod_start - cur)
            cur += mod_start - cur

        transfer_n_frames(
            cap,
            out,
            mod_end - cur,
            lambda frame: blur_image_video_detection(frame, timeframe.segments),
        )
        cur += mod_end - cur

    transfer_n_frames(cap, out, total - cur)


def create_video_writer(cap, out_filename: str):
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
    size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    return cv2.VideoWriter(out_filename, fourcc, cap.get(cv2.CAP_PROP_FPS), size)


def blur_video(cap, output_file, segments: List[VideoDetection]):
    if cap.isOpened() == False:
        print("Error opening video stream or file")
        raise

    out = create_video_writer(cap, output_file)
    fs_segments = merge_video_detections(segments)
    blur_from_timeframes(cap, fs_segments, out)
    out.release()
    cap.release()


if __name__ == "__main__":

    seg1 = VideoDetection(
        time_start=0, time_end=3, corner_1=[590, 730], corner_2=[730, 570]
    )
    seg2 = VideoDetection(
        time_start=0, time_end=23, corner_1=[1090, 630], corner_2=[1630, 170]
    )
    seg3 = VideoDetection(
        time_start=20, time_end=25, corner_1=[1290, 730], corner_2=[1730, 370]
    )

    const_video_file = "/home/vlasov/folder/pyfilter/hackathon_part_1.mp4"
    const_output_file = "/home/vlasov/folder/pyfilter/hackathon_part_1_out.mp4"
    cap = cv2.VideoCapture(const_video_file)

    blur_video(cap, const_output_file, [seg1, seg2, seg3])
