"""
Validator module for external API responses.

This module's classes validate the structure of data retrieved from:
1. dictionaryapi.dev

It ensures that responses contain the required fields and are formatted correctly
before being processed by the parser.

Classes:
    Validator (ABC)
        Abstract base class defining the interface for response validators.
    DictApiValidator(Validator)
        Concrete implementation that validates responses from dictionaryapi.dev.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple, TypedDict

from requests import Response

# ==================================================================================================
# Constants
# ==================================================================================================
REQUIRED_FIELDS = (
    "word",
    "meanings",
)


# ==================================================================================================
# Validator Classes
# ==================================================================================================
class Validator(ABC):
    """Abstract base class for validating API responses.

    This class defines the interface for validators that check the structure
    and content of API responses. Subclasses must implement `validate_response`
    to enforce specific validation rules.

    Methods:
        validate_response() -> True:
            Validates the API response. Returns True if the response matches
            the expected structure. Otherwise raises custom exception.

    """

    @abstractmethod
    def __init__(self, response: Response) -> None: ...

    @abstractmethod
    def validate_response(self) -> bool: ...


class DictApiValidator(Validator):
    """This validator enforces presence of the required top-level fields (word, meanings).

    Expected dictionaryapi.dev response format:
        [
            {
                "word": "string",  REQUIRED
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
                                "definition": "string",  REQUIRED AT LEAST ONE
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
        self._json_data = self._response.json() or {}

    def validate_response(self) -> bool:
        """
        Orchestrates predicate private methods to validate the response structure.

        Calls the following checks in order:
            - _has_ok_status_code: verifies that the HTTP status code indicates success.
            - _is_list: checks that the response JSON is a list.
            - _is_not_empty: ensures the response list is not empty.
            - _is_dict: checks that the first entry in the list is a dictionary.
            - _has_required_fields: ensures required fields ("word", "meanings") are present.
            - _has_word: validates that the "word" field is a non-empty string.
            - _has_meanings: validates that the "meanings" field is a non-empty list.
            - _has_definitions: ensures each meaning contains a "definitions" list.
            - _has_at_least_one_definition: ensures each "definitions" list contains at least
              one non-empty "definition".

        Raises:
            ResponseValidationError: If any validation step fails.

        Returns:
            bool: True if all checks pass.
        """

        if not self._has_ok_status_code():
            raise ResponseValidationError(
                "Invalid HTTP status code.",
                details={"status_code": self._response.status_code},
            )

        if not self._is_list():
            raise ResponseValidationError(
                "Response root must be a list.",
                details={"actual_type": type(self._json_data).__name__},
            )

        if not self._is_not_empty():
            raise ResponseValidationError("Response list is empty.")

        entry = self._json_data[0]

        if not self._is_dict(entry):
            raise ResponseValidationError(
                "First entry must be a dictionary.",
                details={"actual_type": type(entry).__name__},
            )

        if not self._has_required_fields(entry, REQUIRED_FIELDS):
            missing_fields = [field for field in REQUIRED_FIELDS if field not in entry]
            raise ResponseValidationError(
                "Missing required fields.",
                details={"missing_fields": missing_fields},
            )

        if not self._has_word(entry):
            raise ResponseValidationError(
                "Invalid or empty 'word' field.",
                details={"word": entry.get("word")},
            )

        if not self._has_meanings(entry):
            raise ResponseValidationError(
                "Invalid or empty 'meanings' field.",
                details={"meanings": entry.get("meanings")},
            )

        if not self._has_definitions(entry):
            raise ResponseValidationError(
                "Missing 'definitions' in meanings.",
                details={"meanings": entry.get("meanings")},
            )

        if not self._has_at_least_one_definition(entry):
            raise ResponseValidationError(
                "Meaning must contain at least one valid definition.",
                details={"meanings": entry.get("meanings")},
            )

        return True

    # ------------------- Predicates -------------------
    def _has_ok_status_code(self) -> bool:
        return 200 <= self._response.status_code < 300

    def _is_list(self) -> bool:
        return isinstance(self._json_data, list)

    def _is_not_empty(self) -> bool:
        return bool(self._json_data)

    def _has_required_fields(self, entry: Entry, fields: Tuple[str, ...]) -> bool:
        return all(field in entry for field in fields)

    def _has_word(self, entry: Entry) -> bool:
        return self._is_non_empty_str(entry.get("word"))

    def _has_meanings(self, entry: Entry) -> bool:
        meanings = entry.get("meanings")
        return self._is_non_empty_list(meanings)

    def _has_definitions(self, entry: Entry) -> bool:
        meanings = entry.get("meanings", [])
        for meaning in meanings:
            if not self._is_dict(meaning):
                return False
            if "definitions" not in meaning:
                return False
        return True

    def _has_at_least_one_definition(self, entry: Entry) -> bool:

        meanings = entry.get("meanings", [])

        for meaning in meanings:
            definitions = meaning.get("definitions", [])
            for definition in definitions:
                if not self._is_dict(definition) and self._is_non_empty_str(
                    definition.get("definition")
                ):
                    return True

            return False

        return True

    # ------------------- Helper Functions -------------------
    @staticmethod
    def _is_dict(obj: Any) -> bool:
        return isinstance(obj, dict)

    @staticmethod
    def _is_non_empty_list(obj: Any) -> bool:
        return isinstance(obj, list) and bool(obj)

    @staticmethod
    def _is_non_empty_str(obj: Any) -> bool:
        return isinstance(obj, str) and bool(obj.strip())


# ==================================================================================================
# Exceptions
# ==================================================================================================
class ResponseValidationError(Exception):
    """Raised when the API response is invalid or unusable, with contextual details."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """
        Args:
            message (str): Description of the validation failure.
            details (dict, optional): Structured context about the failure.
        """

        super().__init__(message)
        self.details = details or {}

    def __str__(self):
        base = super().__str__()
        if self.details:
            return f"{base} | Details: {self.details}"
        return base


# ==================================================================================================
# TypeDicts
# ==================================================================================================
class Definition(TypedDict):
    """Definition field type structure. Needed for Meaning."""

    definition: str
    example: Optional[str]
    synonyms: List[str]
    antonyms: List[str]


class Meaning(TypedDict):
    """Meaning field type structure. Needed for Entry."""

    partOfSpeech: str
    definitions: List[Definition]


class Phonetic(TypedDict):
    """Phonetic field type structure. Needed for Entry."""

    text: str
    audio: Optional[str]


class Entry(TypedDict):
    """
    Entry field type structure.

    Entry is the top-level response list returned by the dictionaryapi.dev.
    (i.e., response[0] for the word).
    """

    word: str
    phonetic: str
    phonetics: List[Phonetic]
    origin: str
    meanings: List[Meaning]
