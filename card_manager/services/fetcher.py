import logging
from abc import ABC, abstractmethod
from typing import Type

import requests
from requests import Response

logger = logging.getLogger(__name__)


class Fetcher(ABC):
    """Abstract base class for fetching word data from an API."""

    @abstractmethod
    def fetch_word(self, word: str) -> Response:
        """Fetch a word from the API."""


class ErrorHandler(ABC):
    """Interface for handling API responses and exceptions."""

    @abstractmethod
    def handle_status(self, response: Response, word: str) -> Response | ExternalAPIError: ...

    @abstractmethod
    def handle_exception(self, word: str, exception: Exception) -> ExternalAPIError: ...


class DictApiFetcher(Fetcher):
    """Fetcher for dictionaryapi.dev"""

    def __init__(self, api_url: str = DICTIONARYAPI_URL):
        self._api_url = api_url

    def fetch_word(self, word: str) -> Response:
        url = f"{self._api_url}{word}"
        response = requests.get(url, timeout=10)
        return response


class DictApiErrorHandler(ErrorHandler):
    """Handles API exceptions and status codes for dictionaryapi.dev"""

    def handle_status(self, response: Response, word: str) -> Response | ExternalAPIError:
        error = StatusErrorFactory.create(response.status_code, word)
        if error:

            logger.warning(
                "Status code %d indicates error for word '%s': %s",
                response.status_code,
                word,
                error,
            )

            return error

        return response

    def handle_exception(self, word: str, exception: Exception) -> ExternalAPIError:
        if isinstance(exception, requests.RequestException):
            logger.error(
                "Network/request error while fetching '%s': %s",
                word,
                exception,
                exc_info=True,
            )
            return ExternalAPIError(f"Network/request error fetching '{word}': {exception}")

        logger.exception("Unexpected error fetching word '%s': %s", word, exception)

        return ExternalAPIError(f"Unexpected error fetching '{word}': {exception}")


class WordService:
    """Orchestrates fetching words and handling errors via fetcher + error handler."""

    def __init__(self, fetcher: Fetcher, error_handler: ErrorHandler):
        self.fetcher = fetcher
        self.error_handler = error_handler

    def get_word(self, word: str) -> Response | ExternalAPIError:
        try:
            response = self.fetcher.fetch_word(word)
            return self.error_handler.handle_status(response, word)

        except (
            requests.ConnectionError,
            requests.Timeout,
            requests.RequestException,
            ExternalAPIError,
            WordNotFoundError,
        ) as e:
            return self.error_handler.handle_exception(word, e)


# ==================================================================================================
# Constants
# ==================================================================================================
DICTIONARYAPI_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


# ==================================================================================================
# Exceptions and Exceptions Factory
# ==================================================================================================


class ExternalAPIError(Exception):
    """Base exception for all fetcher-related API errors."""


class WordNotFoundError(ExternalAPIError):
    """Raised when a word is not found in the API."""

    def __init__(self, word: str) -> None:
        self.word = word
        super().__init__(f"Word '{word}' not found in dictionary API.")


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
        for code_range, exc_class in cls.STATUS_MAP:
            if status_code in code_range:
                # Special handling for WordNotFoundError
                if exc_class is WordNotFoundError:
                    return exc_class(word)
                return exc_class(f"Error {status_code} for word '{word}'")
        return None
