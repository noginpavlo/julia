"""
This module handles busyness logic of Julia.
It inclutes retrieving data from 3rd party API, processing the data.
It implements sm2 algorithm and handles the algorithmic data to highler-level of abstraction.

====================================================================================
This is a mock module dockstring, make it better as soon as you complete the module.
====================================================================================

Response structure of dictionaryapi.dev:

[
    {
    "word": "string",
    "phonetic": "string",
    "phonetics": [
        {
        "text": "string",
        "audio": "string (optional)" => usually a url
        }
    ],
    "origin": "string",
    "meanings": [
        {
        "partOfSpeech": "string",  => can include 2 or more parts of speech: noun, verb, etc.
        "definitions": [
            {
            "definition": "string",
            "example": "string (optional)",
            "synonyms": ["string"],
            "antonyms": ["string"]
            }
        ]
        }
    ]
    }
]
"""

import json
from abc import ABC, abstractmethod
from collections.abc import Generator

import requests
from requests import Response

# from card_manager.models import Card, Deck


class WordNotFoundError(Exception):
    def __init__(self, word):
        self.word = word
        super().__init__(
            f"Data not available for word {word}. Are you sure you spelled '{word}' correctly?"
        )


class BaseWordDataFetcher(ABC):
    """Interface for DataGetter class. DataGetter must have get_data method."""

    @abstractmethod
    def fetch_word_data(self, word: str, api_url: str) -> Response: ...


class WordDataFetcher(BaseWordDataFetcher):  # consider renaming to sth like DictionaryApiFetcher
    """
    Concrete class that requests data from dictionaryapi.dev.
    Returns response that contains word definitions, examples and transcription.

    Preconditions:
    => The word is a string.
    => api_url is a string.
    """

    def fetch_word_data(self, word: str, api_url: str) -> Response:
        word_url = f"{api_url}{word}"
        response = requests.get(word_url, timeout=None)

        # json_response = response.json()
        # print(json.dumps(json_response, indent=4))

        if (
            response.status_code == 404
        ):  # this might not be correct lvl of abstraction to handle this
            raise WordNotFoundError(word)  # rase this exception in the caller for view to handle

        return response


DICTIONARYAPI_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"
data_fetcher = WordDataFetcher()
data_fetcher.fetch_word_data("branch", DICTIONARYAPI_URL)


class BaseWordDataProcessor(ABC):
    """
    This is an interface for WordDataProcessor.
    """

    @staticmethod
    @abstractmethod
    def _parse_audio(entry: dict) -> str | None: ...

    @staticmethod
    @abstractmethod
    def _parse_definition(entry: dict) -> dict: ...

    @abstractmethod
    def parse_word_data(self) -> dict: ...


class WordDataProcessor(BaseWordDataProcessor):

    def __init__(self, response: Response) -> None:
        self._response = response

    @staticmethod
    def _parse_audio(entry: dict) -> str | None:

        phonetics = entry.get("phonetics")
        if phonetics:
            audio = phonetics.get("audio")
            if isinstance(audio, str) and audio:
                return audio

        return None

    @staticmethod
    def _parse_definition(entry: dict) -> dict:

        meanings = entry.get("meanings")
        definitions: dict = {}
        if meanings:
            for part_of_speech in meanings:
                part_name = part_of_speech.get("partOfSpeech")
                definition_block = part_of_speech.get("definitions")
                definitions[part_name] = list(definition for definition in definition_block)[0:2]

        print(definitions)
        return definitions

    def parse_word_data(self) -> dict:
        """
        This function processes and saves data.
        It can do processing and leave saving data to a view, for example.
        """

        entry = self._response[0]

        word = entry.get("word", "")
        phonetic = entry.get("phonetic", "")
        audio = self._parse_audio(entry)
        definitions: dict = self._parse_definition(entry)
        examples: list = []

        cleaned_data = {
            "word": word,
            "phonetic": phonetic,
            "audio": audio,
            "definitions": definitions,
            "examples": examples,
        }

        return cleaned_data


# def save_data(response, deck_name, user):  # this must accept deck object as an argument
#
#     cleaned_data = {
#         "word": word,
#         "phonetic": phonetic,
#         "audio": audio,
#         "definitions": definitions,
#         "examples": examples,
#     }
#
#     # ROLE 2: Creates card.
#     Card.objects.create(
#         deck=deck,
#         json_data=cleaned_data,
#         word=word,
#     )
#     return word if word else "success"  # return strings?
#
#
# def get_and_save(input_word, deck_name, user):
#
#     try:
#         response = get_data(input_word)
#         return save_data(response.json(), deck_name, user)
#     except WordNotFoundError as e:
#         return str(e)  # raise error and leave it to handle at the correct lvl of abstraction
