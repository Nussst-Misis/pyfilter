#!/usr/bin/env python3
# coding --utf-8--

from speech_to_text_vosk import VoskSpeechToText

if __name__ == "__main__":
    vosk_model = VoskSpeechToText()
    vosk_model.get_text_from_audio(
        "file:///home/ristle/Programming/speech-to-text/fr/audio/my_result.wav")
