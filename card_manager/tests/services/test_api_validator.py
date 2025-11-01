# from types import SimpleNamespace
#
# import pytest
# from requests.models import Response
# from card_manager.services.validator import DictApiValidator, Entry, ResponseValidationError
#
#
# # ------------------- Helper to mock Response -------------------
# def make_response(status_code=200, json_data=None):
#     """Create a mock Response object with given status code and JSON data."""
#     mock_resp = SimpleNamespace()
#     mock_resp.status_code = status_code
#     mock_resp.json = lambda: json_data
#     return mock_resp
#
#
# # ------------------- Sample valid entry -------------------
# VALID_ENTRY = [
#     {
#         "word": "test",
#         "phonetic": "tɛst",
#         "phonetics": [{"text": "tɛst", "audio": ""}],
#         "origin": "Latin",
#         "meanings": [
#             {
#                 "partOfSpeech": "noun",
#                 "definitions": [
#                     {
#                         "definition": "A procedure to assess something.",
#                         "example": "This is a test.",
#                         "synonyms": [],
#                         "antonyms": [],
#                     }
#                 ],
#             }
#         ],
#     }
# ]
#
#
# # ------------------- Test Cases -------------------
# def test_validate_response_success():
#     """Validator returns True for a valid response."""
#     response = make_response(json_data=VALID_ENTRY)
#     validator = DictApiValidator(response)
#     assert validator.validate_response() is True
#
#
# def test_invalid_status_code():
#     """Validator raises error for non-2xx status code."""
#     response = make_response(status_code=404, json_data=VALID_ENTRY)
#     validator = DictApiValidator(response)
#     with pytest.raises(ResponseValidationError) as exc_info:
#         validator.validate_response()
#     assert "Invalid HTTP status code" in str(exc_info.value)
#
#
# def test_response_not_list():
#     """Validator raises error if JSON root is not a list."""
#     response = make_response(json_data={"word": "test"})
#     validator = DictApiValidator(response)
#     with pytest.raises(ResponseValidationError) as exc_info:
#         validator.validate_response()
#     assert "Response root must be a list" in str(exc_info.value)
#
#
# def test_empty_list():
#     """Validator raises error if response list is empty."""
#     response = make_response(json_data=[])
#     validator = DictApiValidator(response)
#     with pytest.raises(ResponseValidationError) as exc_info:
#         validator.validate_response()
#     assert "Response list is empty" in str(exc_info.value)
#
#
# def test_first_entry_not_dict():
#     """Validator raises error if first entry is not a dict."""
#     response = make_response(json_data=[42])
#     validator = DictApiValidator(response)
#     with pytest.raises(ResponseValidationError) as exc_info:
#         validator.validate_response()
#     assert "First entry must be a dictionary" in str(exc_info.value)
#
#
# def test_missing_required_fields():
#     """Validator raises error if 'word' or 'meanings' is missing."""
#     bad_entry = [{"phonetic": "tɛst", "meanings": []}]
#     response = make_response(json_data=bad_entry)
#     validator = DictApiValidator(response)
#     with pytest.raises(ResponseValidationError) as exc_info:
#         validator.validate_response()
#     assert "Missing required fields" in str(exc_info.value)
#
#
# def test_empty_word_field():
#     """Validator raises error if 'word' is empty."""
#     bad_entry = [{"word": "", "phonetic": "tɛst", "meanings": []}]
#     response = make_response(json_data=bad_entry)
#     validator = DictApiValidator(response)
#     with pytest.raises(ResponseValidationError) as exc_info:
#         validator.validate_response()
#     assert "Invalid or empty 'word' field" in str(exc_info.value)
#
#
# def test_empty_meanings_field():
#     """Validator raises error if 'meanings' is empty."""
#     bad_entry = [{"word": "test", "phonetic": "tɛst", "meanings": []}]
#     response = make_response(json_data=bad_entry)
#     validator = DictApiValidator(response)
#     with pytest.raises(ResponseValidationError) as exc_info:
#         validator.validate_response()
#     assert "Invalid or empty 'meanings' field" in str(exc_info.value)
#
#
# def test_missing_definitions():
#     """Validator raises error if a meaning does not have 'definitions'."""
#     bad_entry = [
#         {
#             "word": "test",
#             "phonetic": "tɛst",
#             "phonetics": [{"text": "tɛst", "audio": ""}],
#             "origin": "Latin",
#             "meanings": [{"partOfSpeech": "noun"}],
#         }
#     ]
#     response = make_response(json_data=bad_entry)
#     validator = DictApiValidator(response)
#     with pytest.raises(ResponseValidationError) as exc_info:
#         validator.validate_response()
#     assert "Missing 'definitions' in meanings" in str(exc_info.value)
#
#
# def test_definition_empty_string():
#     """Validator raises error if definitions exist but are empty strings."""
#     bad_entry = [
#         {
#             "word": "test",
#             "phonetic": "tɛst",
#             "phonetics": [{"text": "tɛst", "audio": ""}],
#             "origin": "Latin",
#             "meanings": [{"partOfSpeech": "noun", "definitions": [{"definition": ""}]}],
#         }
#     ]
#     response = make_response(json_data=bad_entry)
#     validator = DictApiValidator(response)
#     with pytest.raises(ResponseValidationError) as exc_info:
#         validator.validate_response()
#     assert "Meaning must contain at least one valid definition" in str(exc_info.value)
