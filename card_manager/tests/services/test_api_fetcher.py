import pytest
from requests.exceptions import ConnectionError, RequestException, Timeout
from requests.models import Response

from card_manager.services.fetcher import (
    DICTIONARYAPI_URL,
    BadRequestError,
    DictApiErrorMapper,
    DictApiFetcher,
    ExternalAPIError,
    ServiceUnavailableError,
    StatusErrorFactory,
    WordNotFoundError,
    WordService,
)


@pytest.fixture
def fetcher():
    return DictApiFetcher()


@pytest.fixture
def error_mapper():
    return DictApiErrorMapper()


@pytest.fixture
def service(fetcher, error_mapper):
    return WordService(fetcher, error_mapper)


def test_fetch_word_success(monkeypatch, fetcher):
    """Test fetching a word returns a Response."""

    class MockResponse:
        status_code = 200

        def json(self):
            return {"word": "example"}

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockResponse())

    response = fetcher.fetch_word("example")
    assert response.status_code == 200
    assert response.json()["word"] == "example"


# -------------------------
# DictApiErrorMapper Tests
# -------------------------
@pytest.mark.parametrize(
    "status_code, expected_exception",
    [
        (400, BadRequestError),
        (404, WordNotFoundError),
        (429, ServiceUnavailableError),
        (500, ServiceUnavailableError),
        (204, ExternalAPIError),
    ],
)
def test_map_status(status_code, expected_exception, error_mapper):
    """Test mapping of HTTP status codes to exceptions."""

    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code

    response = MockResponse(status_code)
    result = error_mapper.map_status(response, "example")

    if isinstance(result, expected_exception):
        if expected_exception is WordNotFoundError:
            assert result.word == "example"
    else:
        assert result == response  # 200 or other non-error


def test_map_exception_requests(error_mapper):
    """Test mapping of requests.RequestException."""
    exc = RequestException("Network error")
    result = error_mapper.map_exception("example", exc)
    assert isinstance(result, ExternalAPIError)
    assert "Network/request error" in str(result)


def test_map_exception_unexpected(error_mapper):
    """Test mapping of unexpected exceptions."""
    exc = ValueError("Unexpected")
    result = error_mapper.map_exception("example", exc)
    assert isinstance(result, ExternalAPIError)
    assert "Unexpected error" in str(result)


# -------------------------
# WordService Tests
# -------------------------
def test_get_word_success(monkeypatch, service):
    """Test WordService returns response for successful fetch."""

    class MockResponse:
        status_code = 200

        def json(self):
            return {"word": "example"}

    monkeypatch.setattr(
        "card_manager.services.fetcher.DictApiFetcher.fetch_word", lambda self, word: MockResponse()
    )

    result = service.get_word("example")
    assert isinstance(result, MockResponse)
    assert result.json()["word"] == "example"


def test_get_word_status_error(monkeypatch, service):
    """Test WordService returns mapped exception for HTTP error."""

    class MockResponse:
        status_code = 404

    monkeypatch.setattr(
        "card_manager.services.fetcher.DictApiFetcher.fetch_word", lambda self, word: MockResponse()
    )

    result = service.get_word("missing")
    assert isinstance(result, WordNotFoundError)
    assert result.word == "missing"


@pytest.mark.parametrize("exc_class", [ConnectionError, Timeout, RequestException])
def test_get_word_request_exceptions(monkeypatch, service, exc_class):
    """Test WordService handles network exceptions."""

    def raise_exc(self, word):
        raise exc_class("Network fail")

    monkeypatch.setattr("card_manager.services.fetcher.DictApiFetcher.fetch_word", raise_exc)

    result = service.get_word("example")
    assert isinstance(result, ExternalAPIError)
    assert "Network/request error" in str(result)
