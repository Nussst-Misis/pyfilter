import wave
from .models import AudioDetection
from typing import List
from scipy.io import wavfile


def reverseInterval(arr, start: int, end: int, fps: int, total: int):
    startFrame = int(fps * start)
    endFrame = int(fps * end)
    arr[startFrame:endFrame] = arr[startFrame:endFrame][::-1]


def CensorAudio(wavFile: str, outFile: str, timeframes: List[AudioDetection]):
    w = wave.open(wavFile, 'rb')
    fps = w.getframerate()
    total = w.getnframes()
    w.close()

    fs, data = wavfile.read(wavFile)
    chans = []
    if len(data.shape) == 1:
        chans = [data]
    elif len(data.shape) == 2:
        chans = [data[:, 0], data[:, 1]]

    for tf in timeframes:
        for chan in chans:
            reverseInterval(chan, tf.time_start, tf.time_end, fps, total)
    wavfile.write(outFile, fs, data)


if __name__ == "__main__":

    tf1 = AudioDetection(time_start=0, time_end=5)
    tf2 = AudioDetection(time_start=7, time_end=10)

    constVideoFile = "/home/vlasov/folder/pyfilter/hackathon_part_1.mp4"
    constWavFile = "/home/vlasov/folder/pyfilter/hackathon_part_1.wav"
    constOutputFile = "/home/vlasov/folder/pyfilter/hackathon_part_1_out.wav"

    CensorAudio(constWavFile, constOutputFile, [tf1, tf2])
