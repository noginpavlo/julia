# =================================================================================================
# 🛠️ Validation section
# Low-level module that validates data retrieved from API provider.
# =================================================================================================
from abc import ABC, abstractmethod

from requests import Response


class ResponseValidator(ABC):
    """Abstract base class for validating API responses.

    Methods:
        validate_response(): Returns True if the response is matches expected structure.
    """

    @abstractmethod
    def __init__(self, response: Response) -> None: ...

    @abstractmethod
    def validate_response(self) -> bool: ...


class DictApiResponseValidator(ResponseValidator):
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

        try:
            data = self._response.json()
        except Exception as e:  # general exception at the top will override all down below?
            raise ValueError(f"Invalid JSON in response: {e}") from e

        if not isinstance(data, list):
            raise TypeError(f"Response must be a list, got {type(data).__name__}")

        if len(data) == 0:
            raise IndexError("Response list is empty - no dictionary entries found")

        entry = data[0]

        if not isinstance(entry, dict):
            raise TypeError(f"Dictionary entry must be a dict, got {type(entry).__name__}")

        required_fields = ["word", "meanings"]

        for field in required_fields:
            if field not in entry:
                raise ValueError(f"Missing required field: '{field}' in dictionary entry")

        word = entry["word"]

        if not isinstance(word, str) or not word.strip():
            raise ValueError(
                f"Field 'word' must be a non-empty string, got {type(word).__name__}: '{word}'"
            )

        meanings = entry["meanings"]

        if not isinstance(meanings, list):
            raise ValueError(f"Field 'meanings' must be a list, got {type(meanings).__name__}")

        if len(meanings) == 0:
            raise ValueError("Field 'meanings' cannot be empty - at least one meaning required")

        return True
