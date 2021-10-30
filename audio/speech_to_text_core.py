import os
import sys
import wave
import json

import pyaudio
import requests
from tqdm import tqdm
from loguru import logger
from urllib.request import urlretrieve
from vosk import Model, KaldiRecognizer, SetLogLevel


class VoskSpeechToText:
    en_us_url = "http://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
    ru_ru_url = "https://alphacephei.com/vosk/models/vosk-model-ru-0.10.zip"

    en_us_small_url = "http://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    ru_ru_small_url = "https://alphacephei.com/vosk/models/vosk-model-ru-0.10.zip"

    @logger.catch
    def __init__(self, model_path: str = "~/.models/speech_to_text", small_model_mode: bool = False):
        self.models = list()

        model_dirs = os.listdir(model_path)

        if len(model_dirs) == 0:
            logger.warn("No models were given")
            if small_model_mode:
                VoskSpeechToText._download_file(self.en_us_small_url)
                VoskSpeechToText._download_file(self.ru_ru_small_url)
            else:
                VoskSpeechToText._download_file(self.en_us_url)
                VoskSpeechToText._download_file(self.ru_ru_url)

        for model in model_dirs:
            self.models.append(Model(model))

    @staticmethod
    @logger.catch
    def _download_file(url: str, destination: str = "~/.models/speech_to_text") -> bool:
        try:
            dst = destination + url.split("/")[-1]
            urlretrieve(url, dst)
        except Exception as e:
            logger.error(f"Failed to download a file. Error message:\n {e}")
            return False

        return True

    @logger.catch
    def __call__(self, audio_url: str) -> [bool, dict]:
        """
        the given result of one model speech to Text
        {'result': [
          # first word in a sentence
          {'conf': 0.84, # confidence
           'end': 4.5, # end time
           'start': 4.05, # start time
           'word': 'test'},
          # then, same parameters for
          # the second word in a sentence
          {'conf': 0.87,
           'end': 5.7,
           'start': 5.1,
           'word': 'library'},
          ... ], # and so on
         # and a full text of the sentence
         'text': 'test library ...'}

        :param audio_url: audio for download
        :return: success code with dict as given in brief with list of models which recognized anything
        """
        VoskSpeechToText._download_file(audio_url, "audio.wav")
        audio_file = VoskSpeechToText.__get_audio("audio.wav")

        models_result = list()
        for model in self.models:
            rec = KaldiRecognizer(model, audio_file.getframerate())
            rec.SetWords(True)
            model_output = self.__recognize_text(audio_file, rec)
            if len(model_output) == 0:
                continue
            models_result.append(model_output)
        if len(models_result) == 0:
            return False, list()
        else:
            return True, models_result

    @logger.catch
    def __recognize_text(self, audio_file, recognition: KaldiRecognizer) -> list:
        results = []

        # recognize speech using vosk model
        while True:
            data = audio_file.readframes(4000)
            if len(data) == 0:
                break
            if recognition.AcceptWaveform(data):
                part_result = json.loads(recognition.Result())
                results.append(part_result)

        part_result = json.loads(recognition.FinalResult())
        results.append(part_result["result"][0])

        return results

    @staticmethod
    @logger.catch
    def __get_audio(self, audio_filename: str) -> [bool, pyaudio.PyAudio]:
        wf = wave.open(audio_filename, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            logger.error("Audio file must be WAV format mono PCM.")
            return wf

        return wf


