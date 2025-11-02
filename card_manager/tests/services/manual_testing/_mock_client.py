"""
Manual testing script (client mocking) for fetcher module.

This module exemplifies how using facade design pattern + pinject library
reduces api boilerplate to minimum.
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
from card_manager.services.service import DictApiModule
from card_manager.services.validator import DictApiValidator

MAX_DEFINITION_MOCK = 2

# usage of fetcher, validator and parser without facade
requests_provider = RequestsProvider()
fetcher = DictApiFetcher(requests_provider, DICTIONARYAPI_URL)
mapper = DictApiErrorMapper()
fetcher_service = WordFetcherService(fetcher, mapper)

response = fetcher_service.get_fetched_word("dog")
validator = DictApiValidator(response)

parser = DictApiParser(response, MAX_DEFINITION_MOCK)
cleaned_data = parser.parse_word_data()
print("########## NO PINJECT #########")
print(json.dumps(cleaned_data, indent=4))


# usage of the same classes with additional facade layer of abstraction + pinject lib
word_service = DictApiModule.get_dict_service()
parsed_data = word_service.get_clean_word("dog")
print("########## PINJECT #########")
print(json.dumps(parsed_data, indent=4))
