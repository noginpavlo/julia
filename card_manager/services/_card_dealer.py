"""
Fetch and process English word data from dictionaryapi.dev.

Features:
- Fetch word data from API.
- Validate API responses.
- Parse definitions, examples, phonetics, and audio links.

Exceptions:
- WordNotFoundError: Raised if the word is not found in the API.
"""

from abc import ABC, abstractmethod
from itertools import islice
from typing import Callable, NotRequired, Required, TypedDict

import time
import pinject
import requests
from pinject import BindingSpec
from requests import Response

DICTIONARYAPI_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


class WordNotFoundError(Exception):
    """Exception raised when a word is not found in API used.

    Attributes:
        word (str): The word that could not be found.
    """

    def __init__(self, word):
        self.word = word
        super().__init__(
            f"Data not available for word {word}. Are you sure you spelled '{word}' correctly?"
        )


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

        response = requests.get(word_url, timeout=None)

        if response.status_code == 404:
            raise WordNotFoundError(word)

        return response


class ResponseValidator(ABC):
    """Abstract base class for validating API responses.

    Subclasses must implement:
        - __init__(response): Store the API response.
        - validate_response(): Check if the response structure is valid.

    Methods:
        validate_response(): Returns True if the response is valid, 
            otherwise raises an exception.
    """

    @abstractmethod
    def __init__(self, response: Response) -> None: ...

    @abstractmethod
    def validate_response(self) -> bool: ...


class DictApiResponseValidator(ResponseValidator):
    """Validate response structure from dictionaryapi.dev.

    Checks if the API response matches the expected structure.

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

        Validates that the response is a non-empty list containing
        dictionaries with required fields like "word" and "meanings".

        Returns:
            bool: True if the response is valid.

        Raises:
            TypeError: If the response or entries are not the expected types.
            ValueError: If required fields are missing or empty.
            IndexError: If the response list is empty.
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


class DefinitionExampleEntry(TypedDict):
    """A single dictionary entry with a definition and optional example.

    Attributes:
        definition (str): The text definition of the word (required).
        example (str | None, optional): Example sentence for the definition.
    """

    definition: Required[str]
    example: NotRequired[str | None]


class ParsedWordData(TypedDict):
    """Complete parsed word data structure from the API response.

    Attributes:
        word (str): The word itself (required).
        phonetic (str, optional): Phonetic transcription of the word.
        audio (str, optional): URL to audio pronunciation.
        definitions_by_pos (dict[str, list[DefinitionExampleEntry]]): 
    """

    word: Required[str]
    phonetic: NotRequired[str | None]
    audio: NotRequired[str | None]
    definitions_by_pos: Required[dict[str, list[DefinitionExampleEntry]]]


class ApiResponseParser(ABC):
    """Abstract base class for parsing API responses into structured word data.

    Subclasses must implement:
        - __init__(response, max_definitions): Store the response and
          maximum number of definitions to parse.
        - parse_word_data(): Extract word data into a ParsedWordData dict.

    Methods:
        parse_word_data(): Returns parsed word data.
    """

    @abstractmethod
    def __init__(self, response: Response, max_definitions: int) -> None: ...

    @abstractmethod
    def parse_word_data(self) -> ParsedWordData:
        """Orchestrates parsing methosds to parse word datat from Response."""


class DictApiParser(ApiResponseParser):
    """Parse dictionaryapi.dev responses into structured word data.

    Extracts word, phonetic transcription, audio link, and definitions
    grouped by part of speech. Limits definitions per part of speech
    using `max_definitions`.

    Methods:
        parse_word_data(): Returns a ParsedWordData dictionary.
    """

    def __init__(self, response: Response, max_definitions: int) -> None:
        self._response = response
        self._max_definitions = max_definitions

    def _parse_audio(self) -> str | None:
        """Extract the first available audio URL from the response.

        Returns:
            str | None: URL of the word's pronunciation audio if available, else None.
        """

        entry = self._response[0]

        phonetics = entry.get("phonetics")
        if phonetics:
            audio = phonetics.get("audio")
            if isinstance(audio, str) and audio:
                return audio

        return None

    def _parse_definitions(self) -> dict[str, list[DefinitionExampleEntry]]:
        """Extract definitions and examples grouped by part of speech.

        Uses `max_definitions` to limit the number of definitions per part of speech.

        Returns:
            dict[str, list[DefinitionExampleEntry]]: Mapping of part-of-speech
            to a list of definition/example entries.
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
        """Parse the API response into structured word data.

        Extracts the word, phonetic transcription, audio link, and
        definitions grouped by part of speech.

        Returns:
            ParsedWordData: Dictionary containing parsed word data.
        """

        entry = self._response[0]
        entry.json()

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
    """Abstract base class for a service that fetches and parses word data.

    Subclasses must implement `get_word_data` to return structured
    word information from a third-party API.

    Methods:
        get_word_data(word): Fetch, validate, and parse data for a given word.
    """

    @abstractmethod
    def get_word_data(self, word: str) -> ParsedWordData:
        """Fetch, validate and parse word data from 3rd party api provider."""


class DictApiService(ApiService):
    """Service to fetch, validate, and parse word data from dictionaryapi.dev.

    Combines a fetcher, validator, and parser to provide structured word data.

    Args:
        fetcher (BaseApiDataFetcher): Object to fetch API responses.
        validator_factory (Callable[[Response], ResponseValidator]): Factory to create a validator.
        parser_factory (Callable[[Response, int], ApiResponseParser]): Factory to create a parser.
        api_url (str, optional): Base URL of the API (default: DICTIONARYAPI_URL).
        max_definitions (int, optional): Max definitions per part of speech (default: 2).

    Methods:
        get_word_data(word): Returns parsed word data for the given word.
    """

    def __init__(
        self,
        fetcher: BaseApiDataFetcher,
        validator_factory: Callable[[Response], ResponseValidator],
        parser_factory: Callable[[Response, int], ApiResponseParser],
        api_url: str = DICTIONARYAPI_URL,
        max_definitions: int = 2,
    ):
        self._fetcher = fetcher
        self._validator_factory = validator_factory
        self._parser_factory = parser_factory
        self._api_url = api_url
        self._max_definitions = max_definitions

    def get_word_data(self, word: str) -> ParsedWordData:
        """Fetch, validate, and parse data for a given word.

        Args:
            word (str): The word to retrieve data for.

        Returns:
            ParsedWordData: Structured word data including definitions,
            phonetic transcription, and audio link.

        Raises:
            WordNotFoundError: If the word is not found by the API.
            ValueError/TypeError/IndexError: If the API response is invalid.
        """

        response = self._fetcher.fetch_word_data(word, self._api_url)

        validator = self._validator_factory(response)
        validator.validate_response()

        parser = self._parser_factory(response, self._max_definitions)
        return parser.parse_word_data()


class DictApiBindings(BindingSpec):
    """Provides dependencies for DictApiService using dependency injection.

    Decouples DictApiService from concrete fetcher, validator, and parser
    implementations by supplying them via factories.

    Methods:
        provide_fetcher(): Returns a concrete BaseApiDataFetcher instance.
        provide_validator_factory(): Returns a factory for ResponseValidator.
        provide_parser_factory(): Returns a factory for ApiResponseParser.
    """

    def provide_fetcher(self) -> BaseApiDataFetcher:
        return DictApiDataFetcher()

    def provide_validator_factory(self) -> Callable[[Response], ResponseValidator]:
        return DictApiResponseValidator

    def provide_parser_factory(self) -> Callable[[Response, int], ApiResponseParser]:
        return DictApiParser


class DictApiModule:
    """Factory for DictApiService with dependencies injected via Pinject.

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
