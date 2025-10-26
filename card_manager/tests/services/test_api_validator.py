from types import SimpleNamespace

import pytest

from card_manager.services.validator import (
    DictApiResponseValidator,
    EmptyResponseError,
    InvalidFieldTypeError,
    MissingFieldError,
)

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def valid_response():
    """Return a mock Response-like object with valid dictionary data."""
    data = [
        {
            "word": "example",
            "phonetic": "ɪɡˈzɑːmpəl",
            "meanings": [
                {
                    "partOfSpeech": "noun",
                    "definitions": [
                        {
                            "definition": "A representative form.",
                            "example": "An example sentence.",
                        }
                    ],
                }
            ],
        }
    ]
    return SimpleNamespace(json=lambda: data)


@pytest.fixture
def empty_list_response():
    """Mock a Response returning an empty list."""
    return SimpleNamespace(json=lambda: [])


@pytest.fixture
def missing_field_response():
    """Mock a Response missing the 'word' field."""
    data = [{"meanings": [{"partOfSpeech": "noun", "definitions": [{"definition": "test"}]}]}]
    return SimpleNamespace(json=lambda: data)


@pytest.fixture
def wrong_type_response():
    """Mock a Response where 'meanings' is not a list."""
    data = [{"word": "hello", "meanings": "not_a_list"}]
    return SimpleNamespace(json=lambda: data)


# ============================================================
# 🧪 Tests for DictApiResponseValidator
# ============================================================


class TestDictApiResponseValidator:
    """Test suite for the DictApiResponseValidator class."""

    def test_valid_response_returns_true(self, valid_response):
        validator = DictApiResponseValidator(valid_response)
        assert validator.validate_response() is True

    def test_empty_response_raises_custom_error(self, empty_list_response):
        validator = DictApiResponseValidator(empty_list_response)
        with pytest.raises(EmptyResponseError):
            validator.validate_response()

    def test_missing_field_raises_custom_error(self, missing_field_response):
        validator = DictApiResponseValidator(missing_field_response)
        with pytest.raises(MissingFieldError):
            validator.validate_response()

    def test_wrong_type_field_raises_custom_error(self, wrong_type_response):
        validator = DictApiResponseValidator(wrong_type_response)
        with pytest.raises(InvalidFieldTypeError):
            validator.validate_response()
