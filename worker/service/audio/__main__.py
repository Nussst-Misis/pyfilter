#!/usr/bin/env python3
# coding --utf-8--

from loguru import logger
from speech_to_text_vosk import VoskSpeechToText

if __name__ == "__main__":
    vosk_model = VoskSpeechToText()
    logger.info(
        vosk_model.get_text_from_audio(
            "file:///home/ristle/Programming/speech-to-text/fr/audio/my_result.wav"
        )
    )
