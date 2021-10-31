#!/usr/bin/env python3
# coding --utf-8--

import os
import shutil
from loguru import logger
from urllib.request import urlretrieve


class SpeechToText:
    @logger.catch
    def _download_file(
        self,
        url: str,
        destination: str = os.getcwd() +
            "/.models/speech_to_text/") -> bool:
        try:
            dst = destination + url.split("/")[-1]
            logger.info(f"String downloading from {url} to {dst}")

            urlretrieve(url, dst)
            if url[-4:] == ".zip":
                logger.info("Downloading done. Starting unzipping...")
                # unzip archive
                shutil.unpack_archive(dst, destination)

                logger.info("Unzipping done. Removing zip files")
                os.remove(dst)
                logger.info("Removed zip archive")
        except Exception as e:
            logger.error(f"Failed to download a file. Error message:\n {e}")
            return False

        return True

    @logger.catch
    def get_text_from_audio(self, audio_url: str,
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

               :param need_to_download: Download or not
               :param audio_url: pyfilter_audio for download
               :return: success code with dict as given in brief with list of models which recognized anything
               """
        raise NotImplementedError
