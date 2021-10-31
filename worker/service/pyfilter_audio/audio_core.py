#!/usr/bin/env python3
# coding --utf-8--

from worker.service.pyfilter_audio import models, speech_to_text_core, ner_module, speech_to_text_vosk
from loguru import logger


class AudioProcess:
    def __init__(
            self,
            speech_to_text_module: speech_to_text_core.SpeechToText = speech_to_text_vosk.VoskSpeechToText()):
        self.ner_module = ner_module.ProcessText()
        self.speech_text = speech_to_text_module

    def __call__(self, audio_url: str, *args, **
                 kwargs) -> [models.AudioResult]:
        audio_result = models.AudioResult
        audio_list = list()

        result, text = self.speech_text.get_text_from_audio(audio_url)
        if not result:
            return audio_result

        for language, list_of_results in text.items():
            for sentence in list_of_results:
                if sentence is not None:
                    for word in sentence.get("result"):
                        founded_persons = self.ner_module(word.get('word'))
                        if len(founded_persons) != 0:
                            result = models.AudioDetection(
                                time_start=word.get("start"), time_end=word.get("end"))
                            logger.debug(
                                f"Forbidden word is {word.get('word')}")

                            audio_list.append(result)
        audio_result.result = audio_list

        return audio_result


if __name__ == "__main__":
    ap = AudioProcess()
    logger.info("String processing 3 minutes of video")
    logger.info(
        ap("/home/ristle/Downloads/hackathon_part_1.mp4").result)
