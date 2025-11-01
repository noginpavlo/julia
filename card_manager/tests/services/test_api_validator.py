
import pytest
from card_manager.services.validator import DictApiValidator, ResponseValidationError

# ------------------- Helpers -------------------

def make_response(status_code=200, data=None):
    """Return ProviderResponse dict with data wrapped in a list."""
    return {"status_code": status_code, "data": [data] if data else []}

# ------------------- Sample valid entry -------------------

VALID_ENTRY = {
    "word": "test",
    "phonetic": "tɛst",
    "phonetics": [{"text": "tɛst", "audio": ""}],
    "origin": "Latin",
    "meanings": [
        {
            "partOfSpeech": "noun",
            "definitions": [
                {
                    "definition": "A procedure to assess something.",
                    "example": "This is a test.",
                    "synonyms": [],
                    "antonyms": [],
                }
            ],
        }
    ],
}

# ------------------- Tests -------------------

def test_validate_response_success():
    validator = DictApiValidator(make_response(data=VALID_ENTRY))
    assert validator.validate_response() is True


def test_invalid_status_code():
    validator = DictApiValidator(make_response(status_code=404, data=VALID_ENTRY))
    with pytest.raises(ResponseValidationError) as exc:
        validator.validate_response()
    assert "Invalid HTTP status code" in str(exc.value)
    assert exc.value.details["status_code"] == 404


def test_empty_list():
    validator = DictApiValidator(make_response(data=None))
    with pytest.raises(ResponseValidationError) as exc:
        validator.validate_response()
    assert "Response list is empty" in str(exc.value)


def test_missing_required_fields():
    bad_entry = {"phonetic": "tɛst", "meanings": []}
    validator = DictApiValidator(make_response(data=bad_entry))
    with pytest.raises(ResponseValidationError) as exc:
        validator.validate_response()
    assert "Missing required fields" in str(exc.value)
    assert "word" in str(exc.value.details["missing_fields"])


def test_empty_word_field():
    bad_entry = {"word": "", "meanings": [{"definitions": [{"definition": "x"}]}]}
    validator = DictApiValidator(make_response(data=bad_entry))
    with pytest.raises(ResponseValidationError) as exc:
        validator.validate_response()
    assert "Invalid or empty 'word' field" in str(exc.value)


def test_empty_meanings_field():
    bad_entry = {"word": "test", "meanings": []}
    validator = DictApiValidator(make_response(data=bad_entry))
    with pytest.raises(ResponseValidationError) as exc:
        validator.validate_response()
    assert "Invalid or empty 'meanings' field" in str(exc.value)


def test_missing_definitions():
    bad_entry = {"word": "test", "meanings": [{"partOfSpeech": "noun"}]}
    validator = DictApiValidator(make_response(data=bad_entry))
    with pytest.raises(ResponseValidationError) as exc:
        validator.validate_response()
    assert "Missing 'definitions' in meanings" in str(exc.value)


def test_definition_empty_string():
    bad_entry = {"word": "test", "meanings": [{"partOfSpeech": "noun", "definitions": [{"definition": ""}]}]}
    validator = DictApiValidator(make_response(data=bad_entry))
    with pytest.raises(ResponseValidationError) as exc:
        validator.validate_response()
    assert "Meaning must contain at least one valid definition" in str(exc.value)
