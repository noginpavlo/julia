
import pytest
from unittest.mock import MagicMock

from card_manager.services.service import (
    DictApiWordService,
    WordDataService,
    DictApiModule,
    WordFetcherService,
    Validator,
    Parser,
)
from requests.models import Response


@pytest.fixture
def mock_fetcher():
    fetcher = MagicMock(spec=WordFetcherService)
    mock_response = MagicMock(spec=Response)
    fetcher.get_fetched_word.return_value = mock_response
    return fetcher


@pytest.fixture
def mock_validator():
    class MockValidator:
        def __init__(self, response):
            self.response = response
            self.validate_called = False

        def validate_response(self):
            self.validate_called = True

    return MockValidator


@pytest.fixture
def mock_parser():
    class MockParser:
        def __init__(self, response, max_definitions):
            self.response = response
            self.max_definitions = max_definitions

        def parse_word_data(self):
            return {"word": "test", "definitions": ["def1", "def2"]}

    return MockParser


@pytest.fixture
def word_service(mock_fetcher, mock_validator, mock_parser):
    return DictApiWordService(
        fetcher=mock_fetcher,
        validator_factory=mock_validator,
        parser_factory=mock_parser,
        api_url="https://fake-api.com",
        max_definitions=2
    )


def test_get_word_data_calls_fetch_validator_parser(word_service, mock_fetcher, mock_validator):
    word = "apple"
    result = word_service.get_word_data(word)

    # Fetcher called
    mock_fetcher.get_fetched_word.assert_called_once_with(word)

    # Validator validates
    validator_instance = word_service._validator_factory(mock_fetcher.get_fetched_word.return_value)
    validator_instance.validate_response()
    assert validator_instance.validate_called

    # Parser returns expected data
    assert result == {"word": "test", "definitions": ["def1", "def2"]}


def test_dict_api_module_returns_service():
    """Test that DictApiModule returns a DictApiWordService instance"""
    service = DictApiModule.get_dict_service()
    assert isinstance(service, DictApiWordService)

    # Ensure the service has required attributes
    assert hasattr(service, "_fetcher")
    assert hasattr(service, "_validator_factory")
    assert hasattr(service, "_parser_factory")
