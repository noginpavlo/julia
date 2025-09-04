"""
====================================================================================
This is a mock module dockstring, make it better as soon as you complete the module.
====================================================================================

Module for fetching and processing English word data from dictionaryapi.dev.

Responsibilities:
- Fetch data from a 3rd-party dictionary API.
- Validate and parse the response into a structured format.
- Extract word definitions, examples, phonetics, and audio links.

Exceptions:
- WordNotFoundError: Raised when the API has no data for the requested word.

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

"""
====================================================================================================
THESE ARE PROBLEMS WITH THIS MODULE:
=> Docstrings are inconcitent and bad. Do considtant styling: Google style, NumPy style. Choose.
=> Separate validation and parsing. How both responsibilities are handled by WordDataProcassor.
=> Definition and example count logic is bad. Use generator and islise to take first n ex. and def.
=> Type hinting verbose?
=> if __name__ == "__main__": guard needed?
====================================================================================================
"""

import json
from abc import ABC, abstractmethod
from itertools import islice
from typing import NotRequired, Required, TypedDict

import requests
from requests import Response

# from card_manager.models import Card, Deck


class WordNotFoundError(Exception):
    def __init__(self, word):
        self.word = word
        super().__init__(
            f"Data not available for word {word}. Are you sure you spelled '{word}' correctly?"
        )


class BaseApiDataFetcher(ABC):
    """Interface for DataGetter class. DataGetter must have get_data method."""

    @abstractmethod
    def fetch_word_data(self, word: str, api_url: str) -> Response: ...


class DictApiDataFetcher(BaseApiDataFetcher):
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

        json_response = response.json()
        print(json.dumps(json_response, indent=4))

        if (
            response.status_code == 404
        ):  # this might not be correct lvl of abstraction to handle this
            raise WordNotFoundError(word)  # rase this exception in the caller for view to handle

        return response


DICTIONARYAPI_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"
data_fetcher = DictApiDataFetcher()
data_fetcher.fetch_word_data("branch", DICTIONARYAPI_URL)


class DefinitionExampleEntry(TypedDict):
    """
    Represents a single dictionary entry for a word’s definition and optional example.

    Fields:
    - definition: The textual definition of the word (required).
    - example: Example sentence illustrating the definition (optional).
    """

    definition: Required[str]
    example: NotRequired[str | None]


class ParsedWordData(TypedDict):
    """Represents the parsed structure of a word from API response.

    Fields:
    - word: The word string (required).
    - phonetic: Phonetic transcription (optional).
    - audio: Optional audio URL (optional).
    - definitions_by_pos: Mapping part-of-speech to a list of DefinitionExampleEntry (required).
    """

    word: Required[str]
    phonetic: NotRequired[str]
    audio: NotRequired[str]
    definitions_by_pos: Required[dict[str, list[DefinitionExampleEntry]]]


class BaseDictApiParser(ABC):
    """
    This is an interface for WordDataProcessor.
    """

    @abstractmethod
    def _validate_entry(self) -> bool: ...

    @abstractmethod
    def _parse_audio(self) -> str | None: ...

    @abstractmethod
    def _parse_definitions(self) -> dict[str, list[DefinitionExampleEntry]]: ...

    @abstractmethod
    def parse_word_data(self) -> dict:
        """Orchestrate parsing methosds to parse word datat from Response."""


class DictApiParser(BaseDictApiParser):

    def __init__(self, response: Response, max_definitions: int, max_examples: int) -> None:
        self._response = response
        self._max_examples = max_examples
        self._max_definitions = max_definitions

    # data validation should be a responsibility of a separate class
    def _validate_entry(self) -> bool:
        """
        Validate dictionary API response structure.

        Args:
            response: API response to validate

        Returns:
            True if valid

        Raises:
            TypeError: If response structure is invalid
            ValueError: If required fields are missing or have wrong types
            IndexError: If response is empty when entry expected
        """

        response = self._response

        if not isinstance(response, list):
            raise TypeError(f"Response must be a list, got {type(response).__name__}")

        if len(response) == 0:
            raise IndexError("Response list is empty - no dictionary entries found")

        entry = response[0]

        if not isinstance(entry, dict):
            raise TypeError(f"Dictionary entry must be a dict, got {type(entry).__name__}")

        required_fields = ["word", "meanings"]

        for field in required_fields:
            if field not in entry:
                raise ValueError(f"Missing required field: '{field}' in dictionary entry")

        word = entry["word"]

        if not isinstance(word, str) or not word.strip():
            raise ValueError(
                f"Field 'word' must be a non-empty string, got {type(word).__name__}: '{word}'"
            )

        meanings = entry["meanings"]

        if not isinstance(meanings, list):
            raise ValueError(f"Field 'meanings' must be a list, got {type(meanings).__name__}")

        if len(meanings) == 0:
            raise ValueError("Field 'meanings' cannot be empty - at least one meaning required")

        return True

    def _parse_audio(self) -> str | None:

        entry = self._response[0]

        phonetics = entry.get("phonetics")
        if phonetics:
            audio = phonetics.get("audio")
            if isinstance(audio, str) and audio:
                return audio

        return None

    def _parse_definitions(self) -> dict[str, list[DefinitionExampleEntry]]:
        """
        Parse dictionary entry to extract definitions and examples per part of speech.
        Uses self._max_definitions and self._max_examples.

        Returns:
            Dictionary structured as:
            {
                "noun": [
                    {"definition": "...", "example": "..."}, (DefinitionExampleEntry)
                    {"definition": "..."}  # example optional (DefinitionExampleEntry)
                ],
                "verb": [
                    ...
                ]
            }
        """

        entry = self._response[0]

        meanings = entry.get("meanings")
        result: dict[str, list[DefinitionExampleEntry]] = {}

        for meaning in meanings:
            pos = meaning.get("partOfSpeech", "unknown_type")
            def_list = meaning.get("definitions")

            def_entry_gen = (
                DefinitionExampleEntry(
                    definition=d["definition"],
                    example=(
                        d.get("example") if d.get("example") and d.get("example").strip() else None
                    ),
                )
                for d in def_list
                if d.get("definition")
            )

            entries_list = list(islice(def_entry_gen, self._max_definitions))

            result[pos] = entries_list

        return result

    def parse_word_data(self) -> dict:
        """
        This function processes and saves data.
        It can do processing and leave saving data to a view, for example.
        """

        entry = self._response[0]

        word = entry.get("word", "")
        phonetic = entry.get("phonetic", "")
        audio = self._parse_audio()
        def_by_pos = self._parse_definitions()

        cleaned_data = {
            "word": word,
            "phonetic": phonetic,
            "audio": audio,
            "definitions_by_pos": def_by_pos,
        }

        return cleaned_data


# def get_and_save(input_word, deck_name, user):
#
#     try:
#         response = get_data(input_word)
#         return save_data(response.json(), deck_name, user)
#     except WordNotFoundError as e:
#         return str(e)  # raise error and leave it to handle at the correct lvl of abstraction
