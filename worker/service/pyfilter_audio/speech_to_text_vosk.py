#!/usr/bin/env python3
# coding --utf-8--

import json
import os
import wave

import pyaudio
from pathlib import Path
from loguru import logger
import moviepy.editor as mp
from pydub import AudioSegment
from .speech_to_text_core import SpeechToText
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)


class VoskSpeechToText(SpeechToText):
    ru_ru_url = "https://alphacephei.com/vosk/models/vosk-model-ru-0.10.zip"
    ru_ru_small_url = "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"

    @logger.catch
    def __init__(
            self,
            model_path: str = os.getcwd() + "/.models/speech_to_text/",
            audio_path: str = os.getcwd() + "/.audio/",
            small_model_mode: bool = True):
        self.models = dict()
        self.model_path = model_path
        self.audio_path = audio_path

        Path(model_path).mkdir(parents=True, exist_ok=True)
        Path(audio_path).mkdir(parents=True, exist_ok=True)

        model_dirs = os.listdir(model_path)

        if len(model_dirs) == 0:
            logger.warning("No models were given")
            logger.info(f"Trying to download in {model_path}")
            if small_model_mode:
                logger.info("Trying to download small models")
                self._download_file(self.ru_ru_small_url, self.model_path)
            else:
                logger.info("Trying to download large models")
                self._download_file(self.ru_ru_url, self.model_path)

        model_dirs = os.listdir(model_path)

        for model in model_dirs:
            full_dst = model_path + model
            if os.path.isdir(full_dst):
                # Only for vosk models
                if full_dst.split("/")[-1][11:][:5] == "small":
                    language = full_dst.split("/")[-1][11:][6:8]
                else:
                    language = full_dst.split("/")[-1][11:][:2]
                self.models[language] = Model(full_dst)

        if len(self.models.items()) == 0:
            raise "No models were given!"

        logger.info("Models inited successfully")

    @logger.catch
    def get_text_from_audio(self, video_url: str,
                            need_to_download: bool = False) -> [bool, dict]:
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
        :param need_to_download: Download or not<
        :param video_url: pyfilter_video for download
        :return: success code with dict as given in brief with list of models which recognized anything
        """
        if need_to_download:
            self._download_file(video_url, self.audio_path)
            audio_file = VoskSpeechToText.__get_audio(
                self.audio_path + video_url.split("/")[-1])
        else:
            audio_file = VoskSpeechToText.__get_audio(video_url)

        models_result = dict()
        try:
            for language, model in self.models.items():
                logger.info(f"Starting detecting using {language} language")
                rec = KaldiRecognizer(model, audio_file.getframerate())
                rec.SetWords(True)

                model_output = self.__recognize_text(audio_file, rec)
                if len(model_output) == 0:
                    continue
                models_result[language] = model_output
                logger.info(f"Converting for {language} language is done")
                logger.debug(self.get_full_test(model_output))
        except Exception as e:
            logger.error(f"Error message is {e}")

        try:
            os.remove(self.audio_path + video_url.split("/")[-1])
        except Exception as e:
            logger.error(f"Error message is {e}")

        if len(models_result) == 0:
            return False, dict()
        else:
            return True, models_result

    @logger.catch
    def get_full_test(self, text_result: list) -> str:
        text = ''
        for r in text_result:
            text += r['text'] if r is not None else ' ' + ' '

        logger.info("\tVosk thinks you said:")
        logger.info(text)
        return text

    @logger.catch
    def __recognize_text(
            self,
            audio_file,
            recognition: KaldiRecognizer) -> list:
        results = []

        # recognize speech using "Voks" model
        while True:
            data = audio_file.readframes(4000)
            if len(data) == 0:
                break
            if recognition.AcceptWaveform(data):
                part_result = json.loads(recognition.Result())
                results.append(part_result)

        part_result = json.loads(recognition.FinalResult())
        results.append(part_result.get("result"))

        return results

    @staticmethod
    @logger.catch
    def __get_audio(video_filename: str) -> [bool, pyaudio.PyAudio]:
        my_clip = mp.VideoFileClip(video_filename)
        if video_filename[:7] == "file://":
            video_filename = video_filename[7:]
        audio_filename = video_filename[:-3] + "wav"

        my_clip.audio.write_audiofile(audio_filename)
        if my_clip.audio.nchannels != 1:
            sound = AudioSegment.from_wav(audio_filename)
            sound = sound.set_channels(1)
            sound.export(audio_filename, format="wav")

        wf = wave.open(audio_filename, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            logger.error("Audio file must be WAV format mono PCM.")
            return wf

        return wf
