"""
Validator module for external API responses.

This module's classes validate the structure of data retrieved from:
1. dictionaryapi.dev

It ensures that responses contain the required fields and are formatted correctly
before being processed by the parser.

Classes:
    ResponseValidator (ABC)
        Abstract base class defining the interface for response validators.
    DictApiResponseValidator(ResponseValidator)
        Concrete implementation that validates responses from dictionaryapi.dev.
"""

from abc import ABC, abstractmethod

from requests import Response


# ==================================================================================================
# 📌 Custom Exceptions
# ==================================================================================================
class ValidationError(Exception):
    """Base exception for API response validation errors."""


class EmptyResponseError(ValidationError):
    """Raised when the response list is empty."""


class MissingFieldError(ValidationError):
    """Raised when a required field is missing in the response."""

    def __init__(self, field_name: str):
        super().__init__(f"Missing required field: '{field_name}'")


class InvalidFieldTypeError(ValidationError):
    """Raised when a field has an unexpected type."""

    def __init__(self, field_name: str, expected_type: str, actual_type: str):
        super().__init__(f"Field '{field_name}' must be of type {expected_type}, got {actual_type}")


# ==================================================================================================
# 🛠 Validator Classes
# ==================================================================================================
class Validator(ABC):
    """Abstract base class for validating API responses.

    This class defines the interface for validators that check the structure
    and content of API responses. Subclasses should implement `validate_response`
    to enforce specific validation rules.

    Methods:
        validate_response() -> bool:
            Validates the API response. Returns True if the response matches
            the expected structure.

    Raises:
        EmptyResponseError:
            Raised when the API response is an empty list or missing required entries.
        MissingFieldError:
            Raised when a required field is missing in the response data.
        InvalidFieldTypeError:
            Raised when a field has a type different from the expected type.
        ValidationError:
            Base class for all validation-related exceptions. Can be raised
            for other generic validation failures.
    """

    @abstractmethod
    def __init__(self, response: Response) -> None: ...

    @abstractmethod
    def validate_response(self) -> bool:
        """Abstract method for response validation."""


class DictApiValidator(Validator):
    """Validate response structure from dictionaryapi.dev.

    Expected response format:
        [
            {
                "word": "string",
                "phonetic": "string",
                "phonetics": [
                    {
                        "text": "string",
                        "audio": "string (optional)"  # usually a URL
                    }
                ],
                "origin": "string",
                "meanings": [
                    {
                        "partOfSpeech": "string",  # can be noun, verb, etc.
                        "definitions": [
                            {
                                "definition": "string",
                                "example": "string (optional)",
                                "synonyms": ["string"],
                                "antonyms": ["string"]
                            }
                        ]
                    }
                ]
            }
        ]
    """

    def __init__(self, response: Response) -> None:
        self._response = response

    def validate_response(self) -> bool:
        """Check if the dictionary API response has the correct structure.

        Returns:
            bool: True if the response matches expected structure.
        """

        json_data = self._response.json()  # propagtes JSONDecodeError => Catch in in orchestrator

        if not isinstance(json_data, list):
            raise InvalidFieldTypeError("response", "list", type(json_data).__name__)
        if len(json_data) == 0:
            raise EmptyResponseError("Response list is empty - no entries found")

        entry = json_data[0]

        if not isinstance(entry, dict):
            raise InvalidFieldTypeError("entry", "dict", type(entry).__name__)

        required_fields = ["word", "meanings"]
        for field in required_fields:
            if field not in entry:
                raise MissingFieldError(field)

        word = entry["word"]
        if not isinstance(word, str) or not word.strip():  # explain why .strip() here is important
            raise InvalidFieldTypeError(
                "word", "non-empty string", type(word).__name__
            )  # this should be missing required field error

        meanings = entry["meanings"]
        if not isinstance(meanings, list) or len(meanings) == 0:
            raise InvalidFieldTypeError(
                "meanings", "non-empty list", type(meanings).__name__
            )  # this should be missing required field error

        return True
