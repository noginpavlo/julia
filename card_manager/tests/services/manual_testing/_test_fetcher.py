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
from card_manager.services.providers import RequestsProvider
from card_manager.services.validator import DictApiValidator

requests_provider = RequestsProvider()
fetcher = DictApiFetcher(requests_provider, DICTIONARYAPI_URL)
mapper = DictApiErrorMapper()
fetcher_service = WordFetcherService(fetcher, mapper)

response = fetcher_service.get_fetched_word("cat")

print(json.dumps(response, indent=4))

validator = DictApiValidator(response)
print(validator.validate_response())
