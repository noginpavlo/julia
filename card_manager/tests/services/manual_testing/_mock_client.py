"""
Manual testing script (client mocking) for fetcher module.
"""

import json

from card_manager.services.fetcher import (
    DICTIONARYAPI_URL,
    DictApiErrorMapper,
    DictApiFetcher,
    WordFetcherService,
)
from card_manager.services.parser import DictApiParser
from card_manager.services.providers import RequestsProvider
from card_manager.services.validator import DictApiValidator

MAX_DEFINITION_MOCK = 2


requests_provider = RequestsProvider()
fetcher = DictApiFetcher(requests_provider, DICTIONARYAPI_URL)
mapper = DictApiErrorMapper()
fetcher_service = WordFetcherService(fetcher, mapper)

response = fetcher_service.get_fetched_word("dog")

# print(json.dumps(response, indent=4))

validator = DictApiValidator(response)
# print(validator.validate_response())

parser = DictApiParser(response, MAX_DEFINITION_MOCK)
cleaned_data = parser.parse_word_data()
print(json.dumps(cleaned_data, indent=4))
