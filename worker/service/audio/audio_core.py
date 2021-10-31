#!/usr/bin/env python3
# coding --utf-8--

from . import speech_to_text_core, ner_module, speech_to_text_vosk
from .. import models
from loguru import logger


class AudioProcess:
    def __init__(
        self,
        speech_to_text_module: speech_to_text_core.SpeechToText = speech_to_text_vosk.VoskSpeechToText(),
    ):
        self.ner_module = ner_module.ProcessText()
        self.speech_text = speech_to_text_module

    def __call__(self, audio_url: str, *args, **kwargs) -> list[models.AudioDetection]:
        audio_list = []

        result, text = self.speech_text.get_text_from_audio(audio_url)
        if not result:
            return audio_list

        for language, list_of_results in text.items():
            for sentence in list_of_results:
                if isinstance(sentence, dict):
                    for word in sentence.get("result", []):
                        founded_persons = self.ner_module(word.get("word"))
                        if len(founded_persons) != 0:
                            result = models.AudioDetection(
                                time_start=word.get("start"), time_end=word.get("end")
                            )
                            logger.debug(f"Forbidden word is {word.get('word')}")

                            audio_list.append(result)
        logger.info(f"Detected audio: {audio_list}")
        return audio_list

