"""
Manual testing script (client mocking) for fetcher module.
"""

from card_manager.services.fetcher import (
    DICTIONARYAPI_URL,
    DictApiErrorMapper,
    DictApiFetcher,
    WordFetcherService,
)
from card_manager.services.providers import RequestsProvider

requests_provider = RequestsProvider()
fetcher = DictApiFetcher(requests_provider, DICTIONARYAPI_URL)
mapper = DictApiErrorMapper()
fetcher_service = WordFetcherService(fetcher, mapper)

result = fetcher_service.get_fetched_word("cat")


print(result)
