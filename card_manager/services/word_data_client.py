"""
Fetch and process English word data from dictionaryapi.dev.

Features:
- Fetch word data from API.
- Validate API responses.
- Parse definitions, examples, phonetics, and audio links.

Exceptions:
- WordNotFoundError: Raised if the word is not found in the API.
"""

import time
import os
import sys
from abc import ABC, abstractmethod
from itertools import islice
from typing import Callable, NotRequired, Required, TypedDict

import pinject  # this liberary might be unneccessery
import requests
from pinject import BindingSpec
from requests import Response

DICTIONARYAPI_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

# Set the default settings module for Django and initialize Django
# (needed for standalone scripts that interact with django)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "julia.settings")
django.setup()


class WordNotFoundError(Exception):
    """Exception raised when a word is not found in API used.

    Attributes:
        word (str): The word that could not be found.
    """

    def __init__(self, word: str) -> None:
        self.word = word
        super().__init__(
            f"Data not available for word {word}. Are you sure you spelled '{word}' correctly?"
        )


# =================================================================================================
# 🛠️ Fetcher section
# Low-level module that fetches data from 3rd party api.
# =================================================================================================


class BaseApiDataFetcher(ABC):
    """Abstract base class for fetching word data from an API.

    Subclasses must implement `fetch_word_data` to return the API response
    for a given word.
    """

    @abstractmethod
    def fetch_word_data(self, word: str, api_url: str) -> Response: ...


class DictApiDataFetcher(BaseApiDataFetcher):
    """Fetches word data from dictionaryapi.dev.

    Methods:
        fetch_word_data(word, api_url): Sends a GET request to the API
            and returns the response. Raises WordNotFoundError if the word
            is not found.
    """

    def fetch_word_data(self, word: str, api_url: str) -> Response:
        word_url = f"{api_url}{word}"

        response = requests.get(word_url, timeout=None)  # consider changing timeout + request retry

        if response.status_code == 404:
            raise WordNotFoundError(word)

        return response


# =================================================================================================
# 🛠️ Validation section
# Low-level module that validates data retrieved from API provider.
# =================================================================================================


class ResponseValidator(ABC):
    """Abstract base class for validating API responses.

    Methods:
        validate_response(): Returns True if the response is matches expected structure.
    """

    @abstractmethod
    def __init__(self, response: Response) -> None: ...

    @abstractmethod
    def validate_response(self) -> bool: ...


class DictApiResponseValidator(ResponseValidator):
    """Validate response structure from dictionaryapi.dev.

    Expected response format:
        [
            {
                "word": "string",
                "phonetic": "string",
                "phonetics": [
                    {
                        "text": "string",
                        "audio": "string (optional)"  # usually a URL
                    }
                ],
                "origin": "string",
                "meanings": [
                    {
                        "partOfSpeech": "string",  # can be noun, verb, etc.
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

    def __init__(self, response: Response) -> None:
        self._response = response

    def validate_response(self) -> bool:
        """Check if the dictionary API response has the correct structure.

        Returns:
            bool: True if the response matches expected structure.
        """

        try:
            data = self._response.json()
        except Exception as e:  # general exception at the top will override all down below?
            raise ValueError(f"Invalid JSON in response: {e}") from e

        if not isinstance(data, list):
            raise TypeError(f"Response must be a list, got {type(data).__name__}")

        if len(data) == 0:
            raise IndexError("Response list is empty - no dictionary entries found")

        entry = data[0]

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


# =================================================================================================
# 🛠️ Parser section
# Low-level module that parses validated data:
#   - removes empty and excessive entries from Response.
#   - defines structure of the data returned to the caller
# =================================================================================================


class DefinitionExampleEntry(TypedDict):
    """A single dictionary entry with a definition and optional example."""

    definition: Required[str]
    example: NotRequired[str | None]


class ParsedWordData(TypedDict):
    """Dictionary structure that the module must return in the end."""

    word: Required[str]
    phonetic: NotRequired[str | None]
    audio: NotRequired[str | None]
    definitions_by_pos: Required[dict[str, list[DefinitionExampleEntry]]]


class ApiParser(ABC):
    """Abstract base class for parsing API responses into ParsedWordData format.

    Methods:
        parse_word_data(): Returns ParsedWordData formatted data.
    """

    @abstractmethod
    def __init__(self, response: Response, max_definitions: int) -> None: ...

    @abstractmethod
    def parse_word_data(self) -> ParsedWordData:
        """Orchestrates parsing methosds to parse word datat from Response."""


class DictApiParser(ApiParser):
    """Parse dictionaryapi.dev responses into ParsedWordData format.

    Extracts word, phonetics , audio link, and definitions grouped by part of speech.
    Limits definitions per part of speech using `max_definitions`.

    Methods:
        parse_word_data(): Returns a ParsedWordData dictionary.
    """

    def __init__(self, response: Response, max_definitions: int) -> None:
        self._response = response
        self._max_definitions = max_definitions

    def _parse_audio(self) -> str | None:
        """Extracts phonetics and the first audio URL from Response."""

        entry = self._response[0]

        phonetics = entry.get("phonetics")
        if phonetics:
            audio = phonetics.get("audio")
            if isinstance(audio, str) and audio:
                return audio

        return None

    def _parse_definitions(self) -> dict[str, list[DefinitionExampleEntry]]:
        """
        Extracts definitions and examples grouped by part of speech, limited by `max_definitions`.
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

    def parse_word_data(self) -> ParsedWordData:
        """Utilizes _parse_audio and _parse_definitions to return ParsedWordData dict.

        Extracts the word, phonetic transcription, audio link, and
        definitions grouped by part of speech.
        """

        entry = self._response[0]

        parsed_data: ParsedWordData = {
            "word": entry.get("word"),
            "phonetic": entry.get("phonetic", ""),
            "audio": self._parse_audio(),
            "definitions_by_pos": self._parse_definitions(),
        }

        return parsed_data


# =================================================================================================
# 🛠️ Services Section
# High-level module that orchestrates mechanical classes.
# =================================================================================================


class ApiService(ABC):
    """
    Abstract base class for a service that orchestrates low-level class methods
    to fetch, validate and parse word data from 3rf party API provider.
    """

    @abstractmethod
    def get_word_data(self, word: str) -> ParsedWordData: ...


class DictApiService(ApiService):
    """Service to fetch, validate, and parse word data from dictionaryapi.dev.

    Args:
        fetcher: Object to fetch API responses.
        validator_factory: Factory to create a validator.
        parser_factory: Factory to create a parser.
        api_url: Base URL of the API (default: DICTIONARYAPI_URL).
        max_definitions: Max definitions per part of speech (default: 2).
    """

    def __init__(
        self,
        fetcher: BaseApiDataFetcher,
        validator_factory: Callable[[Response], ResponseValidator],
        parser_factory: Callable[[Response, int], ApiParser],
        api_url: str = DICTIONARYAPI_URL,
        max_definitions: int = 2,
    ):
        self._fetcher = fetcher
        self._validator_factory = validator_factory
        self._parser_factory = parser_factory
        self._api_url = api_url
        self._max_definitions = max_definitions

    def get_word_data(self, word: str) -> ParsedWordData:
        """Fetch, validate, and parse data for a given word."""

        response = self._fetcher.fetch_word_data(word, self._api_url)

        validator = self._validator_factory(response)
        validator.validate_response()

        parser = self._parser_factory(response, self._max_definitions)
        return parser.parse_word_data()


# do you really need to use DI libefary to satisfy DIP ones?
class DictApiBindings(BindingSpec):
    """Provides dependencies for DictApiService using DI library Pinject.

    Decouples DictApiService from concrete fetcher, validator, and parser
    implementations by supplying them via factories.

    Methods:
        provide_fetcher(): Returns a concrete BaseApiDataFetcher instance.
        provide_validator_factory(): Returns a factory for ResponseValidator.
        provide_parser_factory(): Returns a factory for ApiParser.
    """

    def provide_fetcher(self) -> BaseApiDataFetcher:
        return DictApiDataFetcher()

    def provide_validator_factory(self) -> Callable[[Response], ResponseValidator]:
        return DictApiResponseValidator

    def provide_parser_factory(self) -> Callable[[Response, int], ApiParser]:
        return DictApiParser


class DictApiModule:
    """Factory for DictApiService with Pinject.

    Provides a single access point to DictApiService, wiring fetcher,
    validator, and parser according to DictApiBindings.

    Methods:
        get_dict_service(): Returns a DictApiService instance with dependencies injected.
    """

    _graph = None

    @classmethod
    def get_dict_service(cls) -> DictApiService:
        if cls._graph is None:
            cls._graph = pinject.new_object_graph(binding_specs=[DictApiBindings()])
        return cls._graph.provide(DictApiService)
