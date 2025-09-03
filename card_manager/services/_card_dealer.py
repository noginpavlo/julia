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

        json_response = response.json()
        print(json.dumps(json_response, indent=4))

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

    @abstractmethod
    def _validate_entry(self) -> bool: ...

    @abstractmethod
    def _parse_audio(self) -> str | None: ...

    @abstractmethod
    def _parse_definitions(self) -> dict[str, dict[str, list[str]]]: ...

    @abstractmethod
    def parse_word_data(self) -> dict:
        """Orchestrate parsing methosds to parse word datat from Response."""


class WordDataProcessor(BaseWordDataProcessor):

    def __init__(self, response: Response, max_definitions: int, max_examples: int) -> None:
        self._response = response
        self._max_examples = max_examples
        self._max_definitions = max_definitions

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

    def _parse_definitions(self) -> dict[str, dict[str, list[str]]]:
        """
        Parse dictionary entry to extract 2 definitions and 2 examples per part of speech.

        Args:
            entry: Dictionary entry from API response

        Returns:
            Dictionary with structure:
            {
                "noun": {
                    "definitions": ["def1", "def2"],
                    "examples": ["ex1", "ex2"]
                },
                "verb": {
                    "definitions": ["def1", "def2"],
                    "examples": ["ex1", "ex2"]
                }
            }
        """

        entry = self._response[0]

        meanings: dict | list = entry.get("meanings", [])
        definitions: dict[str, dict[str, list[str]]] = {}

        for meaning in meanings:
            part_of_speech = meaning.get("partOfSpeech", "word")

            definitions_list = meaning.get("definitions", [])
            definitions[part_of_speech] = {"definitions": [], "examples": []}

            # the counters approach must be changed to something better. (generators?)
            definitions_count = 0
            examples_count = 0

            for definition_obj in definitions_list:

                if definitions_count < self._max_definitions:
                    definition_text = definition_obj.get("definition")
                    if definition_text:
                        definitions[part_of_speech]["definitions"].append(definition_text)
                        definitions_count += 1

                if examples_count < 2:
                    example_text = definition_obj.get("example")
                    if example_text and example_text.strip():
                        definitions[part_of_speech]["examples"].append(example_text.strip())
                        examples_count += 1

                if definitions_count >= 2 and examples_count >= 2:
                    break

        return definitions

    def parse_word_data(self) -> dict:
        """
        This function processes and saves data.
        It can do processing and leave saving data to a view, for example.
        """

        entry = self._response[0]

        word = entry.get("word", "")
        phonetic = entry.get("phonetic", "")
        audio = self._parse_audio()
        definitions = self._parse_definitions()

        cleaned_data = {
            "word": word,
            "phonetic": phonetic,
            "audio": audio,
            "definitions": definitions,
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
