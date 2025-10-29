# =================================================================================================
# 🛠️ Services Section
# High-level module that orchestrates mechanical classes.
# =================================================================================================
from abc import ABC, abstractmethod
from typing import Callable

import pinject  # this library might be unneccessery
from pinject import BindingSpec
from requests import Response

from .fetcher import DICTIONARYAPI_URL, DictApiFetcher, Fetcher
from .parser import DictApiParser, ParsedWordData, Parser
from .validator import DictApiValidator, Validator


class Service(ABC):
    """
    Abstract base class for a service that orchestrates low-level class methods
    to fetch, validate and parse word data from 3rf party API provider.
    """

    @abstractmethod
    def get_clean_word(self, word: str) -> ParsedWordData: ...


class DictApiService(Service):
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
        fetcher: Fetcher,
        validator_factory: Callable[[Response], Validator],
        parser_factory: Callable[[Response, int], Parser],
        api_url: str = DICTIONARYAPI_URL,
        max_definitions: int = 2,
    ):
        self._fetcher = fetcher
        self._validator_factory = validator_factory
        self._parser_factory = parser_factory
        self._api_url = api_url
        self._max_definitions = max_definitions

    def get_clean_word(self, word: str) -> ParsedWordData:
        """
        Fetch, validate, and parse data for a given word.
        Returns clean word data ready for db recording.
        """

        response = self._fetcher.fetch_word(word, self._api_url)

        validator = self._validator_factory(response)
        validator.validate_response()

        parser = self._parser_factory(response, self._max_definitions)
        return parser.parse_word()


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

    def provide_fetcher(self) -> Fetcher:
        return DictApiFetcher()

    def provide_validator_factory(self) -> Callable[[Response], Validator]:
        return DictApiValidator

    def provide_parser_factory(self) -> Callable[[Response, int], Parser]:
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
