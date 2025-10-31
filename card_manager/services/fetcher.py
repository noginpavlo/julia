"""
Module for fetching dictionary word data from third-party APIs.

It provides:
- Fetcher classes to retrieve word data from the API.
- Error mappers to translate API responses and exceptions into domain-specific errors.
- A service class to orchestrate fetching words and handling errors.

Exceptions:
- ExternalAPIError: Base exception for all fetcher-related API errors.
- WordNotFoundError: Raised when a requested word is not found.
- BadRequestError: Raised for invalid requests (HTTP 400–403).
- ServiceUnavailableError: Raised when the API is unavailable (HTTP 5xx or 429).

Usage example:
    >>> fetcher = DictApiFetcher()
    >>> error_mapper = DictApiErrorMapper()
    >>> service = WordService(fetcher, error_mapper)
    >>> result = service.get_word("example")
"""

from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Type
import requests
from requests import Response

logger = logging.getLogger(__name__)

# ==================================================================================================
# Constants
# ==================================================================================================
DICTIONARYAPI_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


# ==================================================================================================
# Fetcher Classes
# ==================================================================================================
class Fetcher(ABC):
    """Abstract base class for fetching word data from an API."""

    @abstractmethod
    def fetch_word(self, word: str) -> Response:
        """Fetch a word from an API."""


class ErrorMapper(ABC):
    """Interface for mapping API responses and exceptions to domain errors."""

    @abstractmethod
    def map_status(self, response: Response, word: str) -> Response | ExternalAPIError: ...

    @abstractmethod
    def map_exception(self, word: str, exception: Exception) -> ExternalAPIError: ...


class DictApiFetcher(Fetcher):
    """Fetcher for dictionaryapi.dev API.

    Performs HTTP GET requests to retrieve word data from dictionaryapi.dev.

    Args:
        api_url (str): Base URL of the dictionary API. Defaults to DICTIONARYAPI_URL.

    Methods:
        fetch_word(word): Fetches the specified word and returns the HTTP response.
    """

    def __init__(self, api_url: str = DICTIONARYAPI_URL):
        self._api_url = api_url

    def fetch_word(self, word: str) -> Response:
        """Fetch the word data from the API.

        Args:
            word (str): The word to fetch data from the dictionaryapi.def for.
        """
        endpoint = f"{self._api_url}{word}"
        response = requests.get(endpoint, timeout=10)
        return response


class DictApiErrorMapper(ErrorMapper):
    """Handles API exceptions and status codes for dictionaryapi.dev"""

    def map_status(self, response: Response, word: str) -> Response | ExternalAPIError:
        """Maps an HTTP response's status code to a domain-specific error.

        Logs a warning if the status indicates an error.

        Args:
            response (Response): The HTTP response to check.
            word (str): The word requested.

        Returns:
            Response: The original response if status is OK.
            ExternalAPIError: Mapped domain error if status indicates a problem.
        """
        status_error = StatusErrorFactory.create(response.status_code, word)
        if status_error:

            logger.warning(
                "Status code %d indicates error for word '%s': %s",
                response.status_code,
                word,
                status_error,
            )

            return status_error

        return response

    def map_exception(self, word: str, exception: Exception) -> ExternalAPIError:
        """Maps raised exception to a domain-specific error. Log it.

        Args:
            word (str): The word being fetched when the exception occurred.
            exception (Exception): The exception.

        Returns:
            ExternalAPIError: Mapped domain error.
        """
        if isinstance(exception, requests.RequestException):
            logger.error(
                "Network/request error while fetching '%s': %s",
                word,
                exception,
                exc_info=True,
            )
            return ExternalAPIError(f"Network/request error fetching '{word}': {exception}")

        logger.exception("Unexpected error fetching word '%s': %s", word, exception)

        return ExternalAPIError(f"Unexpected error when fetching '{word}': {exception}")


class WordService:
    """Orchestrates fetching words and handling errors via fetcher + error handler."""

    def __init__(self, fetcher: Fetcher, error_handler: ErrorMapper):
        self.fetcher = fetcher
        self.error_handler = error_handler

    def get_word(self, word: str) -> Response | ExternalAPIError:
        """Fetch a word and return the response or a mapped domain error.

        Args:
            word (str): The word to fetch.

        Returns:
            Response: The API response if successful.
            ExternalAPIError: Mapped error if fetching or status check fails.
        """
        try:
            response = self.fetcher.fetch_word(word)
            return self.error_handler.map_status(response, word)
        except (
            requests.ConnectionError,
            requests.Timeout,
            requests.RequestException,
            ExternalAPIError,
            WordNotFoundError,
        ) as e:
            return self.error_handler.map_exception(word, e)


# ==================================================================================================
# Exceptions and Exceptions Factory
# ==================================================================================================
class ExternalAPIError(Exception):
    """Base exception for all fetcher-related API errors."""


class WordNotFoundError(ExternalAPIError):
    """Raised when a word is not found in the API."""

class BadRequestError(ExternalAPIError):
    """Raised when request is invalid (HTTP 400–403)."""


class ServiceUnavailableError(ExternalAPIError):
    """Raised when API server is unavailable (HTTP 5xx or 429)."""


class StatusErrorFactory:
    """Maps HTTP status codes to appropriate exception classes."""

    STATUS_MAP: list[tuple[range, Type[ExternalAPIError]]] = [
        (range(400, 404), BadRequestError),
        (range(404, 405), WordNotFoundError),
        (range(429, 430), ServiceUnavailableError),
        (range(500, 600), ServiceUnavailableError),
        (range(204, 205), ExternalAPIError),
    ]

    @classmethod
    def create(cls, status_code: int, word: str) -> ExternalAPIError | None:
        """Return the exception corresponding to a status code, or None if successful.

        Args:
            status_code (int): HTTP status code from the API response.
            word (str): The word that was requested.

        Returns:
            ExternalAPIError or None: The mapped domain-specific exception, or None if no error.
        """
        for code_range, exception_class in cls.STATUS_MAP:
            if status_code in code_range:
               return exception_class(f"Error {status_code} for word '{word}'")

        return None
