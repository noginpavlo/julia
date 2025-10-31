"""
Providers for fetching word data, abstracting the requests library.

- Provider: interface for any data source.
- RequestsProvider: concrete implementation for requests.

Purpose: decouple business logic from the HTTP library.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import requests

from card_manager.services.fetcher import ProviderResponse


class Provider(ABC):
    """Abstraction for any source of word data."""

    @abstractmethod
    def get_word_data(self, endpoint: str) -> ProviderResponse: ...


class RequestsProvider(Provider):
    """Fetch word data using the requests library."""

    def get_word_data(self, endpoint: str) -> ProviderResponse:
        """Fetch data from api and return ProviderResponse."""
        response = requests.get(str(endpoint), timeout=10)

        return ProviderResponse(data=response.json(), status_code=response.status_code)
