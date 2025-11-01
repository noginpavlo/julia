from unittest.mock import Mock, patch

import pytest
import requests

from card_manager.services.providers import Provider, RequestsProvider

# ---------------------------
# Test Provider abstract base
# ---------------------------


def test_provider_is_abstract():
    """Provider should not be instantiable because it's abstract."""
    with pytest.raises(TypeError):
        Provider()


# ---------------------------
# Test RequestsProvider
# ---------------------------


@pytest.fixture
def endpoint():
    return "https://fakeapi.com/word/example"


@pytest.fixture
def mock_success_response():
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"word": "example"}
    return mock_resp

def test_get_word_data_network_error(endpoint):
    """RequestsProvider raises ConnectionError on network failure."""
    provider = RequestsProvider()
    with patch(
        "card_manager.services.providers.requests.get",
        side_effect=requests.ConnectionError("Network down"),
    ):
        with pytest.raises(requests.ConnectionError):
            provider.get_word_data(endpoint)


def test_get_word_data_invalid_json(endpoint):
    """RequestsProvider raises ValueError if JSON is invalid."""
    provider = RequestsProvider()
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.side_effect = ValueError("Invalid JSON")

    with patch("card_manager.services.providers.requests.get", return_value=mock_resp):
        with pytest.raises(ValueError):
            provider.get_word_data(endpoint)
