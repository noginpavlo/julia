import pytest
from card_manager.services.parser import DictApiParser

# ------------------- Sample entries -------------------

VALID_ENTRY = {
    "word": "test",
    "phonetic": "tɛst",
    "phonetics": [{"text": "tɛst", "audio": "https://audio.test/test.mp3"}],
    "origin": "Latin",
    "meanings": [
        {
            "partOfSpeech": "noun",
            "definitions": [
                {"definition": "A procedure to assess something.", "example": "This is a test."},
                {"definition": "Another definition without example."},
            ],
        },
        {
            "partOfSpeech": "verb",
            "definitions": [
                {"definition": "To carry out a test."}
            ],
        },
    ],
}

ENTRY_WITH_EMPTY_DEFINITION = {
    "word": "example",
    "phonetic": "ɪgˈzɑːmpəl",
    "phonetics": [{"text": "ɪgˈzɑːmpəl", "audio": ""}],
    "meanings": [
        {
            "partOfSpeech": "noun",
            "definitions": [
                {"definition": ""},  # empty definition should be skipped
                {"definition": "A representative instance."},
            ],
        }
    ],
}

ENTRY_WITH_NO_PHONETICS = {
    "word": "empty",
    "phonetic": "",
    "phonetics": [],
    "meanings": [
        {"partOfSpeech": "noun", "definitions": [{"definition": "Nothingness"}]}
    ],
}

# ------------------- Helper -------------------

def make_response(entry):
    """Wraps entry in ProviderResponse dict."""
    return {"status_code": 200, "data": entry}


# ------------------- Tests -------------------

def test_parse_word_basic():
    parser = DictApiParser(make_response(VALID_ENTRY), max_definitions=5)
    result = parser.parse_word_data()
    assert result["word"] == "test"
    assert result["phonetic"] == "tɛst"
    assert result["audio"] == "https://audio.test/test.mp3"
    assert "noun" in result["definition_by_part_of_speech"]
    assert "verb" in result["definition_by_part_of_speech"]


def test_group_definitions_by_part_of_speech():
    parser = DictApiParser(make_response(VALID_ENTRY), max_definitions=5)
    result = parser.parse_word_data()
    noun_defs = result["definition_by_part_of_speech"]["noun"]
    assert len(noun_defs) == 2
    assert all(isinstance(d, dict) for d in noun_defs)
    assert noun_defs[0]["definition"] == "A procedure to assess something."
    assert noun_defs[0]["example"] == "This is a test."
    assert noun_defs[1]["definition"] == "Another definition without example."
    assert noun_defs[1]["example"] is None  # missing example


def test_max_definitions_limit():
    parser = DictApiParser(make_response(VALID_ENTRY), max_definitions=1)
    result = parser.parse_word_data()
    noun_defs = result["definition_by_part_of_speech"]["noun"]
    assert len(noun_defs) == 1  # limited to 1
    assert noun_defs[0]["definition"] == "A procedure to assess something."


def test_empty_definitions_skipped():
    parser = DictApiParser(make_response(ENTRY_WITH_EMPTY_DEFINITION), max_definitions=5)
    result = parser.parse_word_data()
    noun_defs = result["definition_by_part_of_speech"]["noun"]
    assert len(noun_defs) == 1
    assert noun_defs[0]["definition"] == "A representative instance."
    assert noun_defs[0]["example"] is None


def test_no_phonetics_audio():
    parser = DictApiParser(make_response(ENTRY_WITH_NO_PHONETICS), max_definitions=5)
    result = parser.parse_word_data()
    assert result["audio"] == ""  # fallback to empty string


def test_missing_part_of_speech_default():
    entry = {
        "word": "foo",
        "phonetic": "",
        "phonetics": [],
        "meanings": [{"definitions": [{"definition": "A test"}]}],  # no partOfSpeech
    }
    parser = DictApiParser(make_response(entry), max_definitions=5)
    result = parser.parse_word_data()
    assert "part_of_speech_unknown" in result["definition_by_part_of_speech"]
    defs = result["definition_by_part_of_speech"]["part_of_speech_unknown"]
    assert defs[0]["definition"] == "A test"
    assert defs[0]["example"] is None

