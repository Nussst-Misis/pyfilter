#!/usr/bin/env python

import os
import json

from loguru import logger
from natasha import (
    Segmenter,
    MorphVocab,

    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,

    PER, ORG, LOC,
    NamesExtractor,

    Doc
)


class ProcessText:
    @logger.catch
    def __init__(
            self,
            celebrities: str = os.getcwd() +
            "/.data/celebrities.json"):
        self.celebrities = json.load(open(celebrities, 'r'))

        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()

        self.emb = NewsEmbedding()
        self.ner_tagger = NewsNERTagger(self.emb)
        self.morph_tagger = NewsMorphTagger(self.emb)
        self.syntax_parser = NewsSyntaxParser(self.emb)
        self.names_extractor = NamesExtractor(self.morph_vocab)

    @staticmethod
    @logger.catch
    def search(ner, data, type: str) -> tuple:
        for info in ner[type]:
            if info["normal"] == data["normal"]:
                return True, info["normal"]
        return False, {}

    @logger.catch
    def __extract_data(self, text: str):
        doc = Doc(text)
        doc.segment(Segmenter())
        doc.tag_morph(self.morph_tagger)

        for token in doc.tokens:
            token.lemmatize(self.morph_vocab)

        doc.parse_syntax(self.syntax_parser)
        doc.tag_ner(self.ner_tagger)

        for span in doc.spans:
            span.normalize(self.morph_vocab)

        forbidden_info = list()

        for fact in doc.spans:
            found = False
            if fact.type == PER:
                found, info = ProcessText.search(
                    self.celebrities, fact.as_json, 'names')
            if found is True:
                forbidden_info.append(fact)

        return forbidden_info

    @logger.catch
    def __call__(self, text: str):
        fi = self.__extract_data(text)
        if fi == list():
            return list()

        output_data = list()
        for data in fi:
            data = data.as_json
            output_data.append({data["start"], data["stop"], data["text"]})

        return output_data


@logger.catch
def getFSM(filename: str = os.getcwd() + "/.data/celebrities.txt") -> list:
    with open(filename, encoding="utf-16") as file:
        lines = file.readlines()
        lines = [line.rstrip().split(",")[-1] for line in lines]

    return lines


@logger.catch
def extractDataFromFSM(
    filename: str = os.getcwd() +
    "/.data/celebrities.txt",
    celebrities: str = os.getcwd() +
        "/.data/celebrities.json"):
    all_data = dict()

    all_data['names'] = list()
    all_data['others'] = list()
    all_data['organizations'] = list()

    celebrities = json.load(open(celebrities, 'r'))

    segmenter = Segmenter()
    morph_vocab = MorphVocab()

    emb = NewsEmbedding()
    ner_tagger = NewsNERTagger(emb)
    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    names_extractor = NamesExtractor(morph_vocab)

    fsm = getFSM(filename)

    for sentence in fsm:
        doc = Doc(sentence)
        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)

        for token in doc.tokens:
            token.lemmatize(morph_vocab)

        doc.parse_syntax(syntax_parser)
        doc.tag_ner(ner_tagger)

        for span in doc.spans:
            span.normalize(morph_vocab)

        for fact in doc.spans:
            if fact.text in celebrities.get('names'):
                continue
            if fact.type == PER:
                all_data['names'].append(fact.as_json)

    return all_data


if __name__ == '__main__':
    # prepared_data = extractDataFromFSM()
    #
    # with open(os.getcwd() + "/.data/celebrities.json", 'w') as f:
    #     json.dump(prepared_data, f, ensure_ascii=False, indent=4)

    pt = ProcessText()
    logger.info("Starting finding persons in selected text:")
    logger.info(f"\t Привет, это же Алан Алда!")
    logger.info(pt("Привет, это же Алан Алда!"))
