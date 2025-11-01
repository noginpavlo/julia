from unittest.mock import Mock

import pytest
import requests

from card_manager.services.fetcher import (
    BadRequestError,
    DictApiErrorMapper,
    DictApiFetcher,
    ExternalAPIError,
    ProviderResponse,
    ServiceUnavailableError,
    WordNotFoundError,
    WordService,
)

# ---------------------------
# Fixtures
# ---------------------------


@pytest.fixture
def word():
    return "example"


@pytest.fixture
def provider_mock():
    return Mock()


@pytest.fixture
def success_response(word):
    return ProviderResponse(data={"word": word}, status_code=200)


@pytest.fixture
def bad_request_response():
    return ProviderResponse(data={}, status_code=400)


@pytest.fixture
def not_found_response():
    return ProviderResponse(data={}, status_code=404)


@pytest.fixture
def service_factory(provider_mock):
    """Helper to create WordService with given provider."""

    def _create():
        fetcher = DictApiFetcher(provider=provider_mock)
        mapper = DictApiErrorMapper()
        return WordService(fetcher, mapper)

    return _create


# ---------------------------
# DictApiFetcher Tests
# ---------------------------


def test_fetch_word_calls_provider(provider_mock, word, success_response):
    """DictApiFetcher should call provider and return its response."""
    provider_mock.get_word_data.return_value = success_response
    fetcher = DictApiFetcher(provider=provider_mock)

    response = fetcher.fetch_word(word)

    provider_mock.get_word_data.assert_called_once_with(
        f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    )
    assert response == success_response


# ---------------------------
# DictApiErrorMapper Tests
# ---------------------------


@pytest.mark.parametrize(
    "status_code,expected_exception",
    [
        (200, None),
        (400, BadRequestError),
        (403, BadRequestError),
        (404, WordNotFoundError),
        (429, ServiceUnavailableError),
        (500, ServiceUnavailableError),
    ],
)
def test_map_status_various_codes(word, status_code, expected_exception):
    mapper = DictApiErrorMapper()
    response = ProviderResponse(data={}, status_code=status_code)

    result = mapper.map_status(response, word)

    if expected_exception:
        assert isinstance(result, expected_exception)
        assert str(word) in str(result)
    else:
        assert result == response


def test_map_exception_requests_error(word):
    mapper = DictApiErrorMapper()
    exc = requests.ConnectionError("Network down")
    result = mapper.map_exception(word, exc)
    assert isinstance(result, ExternalAPIError)
    assert "Network/request error" in str(result)


def test_map_exception_generic_error(word):
    mapper = DictApiErrorMapper()
    exc = ValueError("Oops")
    result = mapper.map_exception(word, exc)
    assert isinstance(result, ExternalAPIError)
    assert "Unexpected error" in str(result)


# ---------------------------
# WordService Tests
# ---------------------------


def test_get_word_success(service_factory, provider_mock, success_response, word):
    provider_mock.get_word_data.return_value = success_response
    service = service_factory()

    result = service.get_word(word)
    assert result == success_response


def test_get_word_status_error(service_factory, provider_mock, bad_request_response, word):
    provider_mock.get_word_data.return_value = bad_request_response
    service = service_factory()

    result = service.get_word(word)
    assert isinstance(result, BadRequestError)


def test_get_word_exception_handling(word):
    class FailingFetcher:
        def fetch_word(self, word):
            raise requests.ConnectionError("Network down")

    service = WordService(FailingFetcher(), DictApiErrorMapper())
    result = service.get_word(word)

    assert isinstance(result, ExternalAPIError)
    assert "Network/request error" in str(result)
