# =================================================================================================
# 🛠️ Fetcher section
# Low-level module that fetches data from 3rd party api.
# =================================================================================================

from abc import ABC, abstractmethod

import requests
from requests import Response

DICTIONARYAPI_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


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


class Fetcher(ABC):
    """Abstract base class for fetching word data from an API.

    Subclasses must implement `fetch_word_data` to return the API response
    for a given word.
    """

    @abstractmethod
    def fetch_word_data(self, word: str, api_url: str) -> Response: ...


class DictApiFetcher(Fetcher):
    """Fetches word data from dictionaryapi.dev.

    Methods:
        fetch_word_data(word, api_url): Sends a GET request to the API
            and returns the response. Raises WordNotFoundError if the word
            is not found.
    """

    def fetch_word_data(self, word: str, api_url: str) -> Response:
        word_url = f"{api_url}{word}"

        response = requests.get(word_url, timeout=None)  # make sure you retry in Celery

        if response.status_code == 404:
            raise WordNotFoundError(word)

        return response
