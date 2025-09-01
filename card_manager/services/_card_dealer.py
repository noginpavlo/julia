"""
This module handles busyness logic of the application.
It inclutes retrieving data from 3rd party API, processing the data.
It implements sm2 algorithm and handles the algorithmic data to highler-level of abstraction.

====================================================================================
This is a mock module dockstring, make it better as soon as you complete the module.
====================================================================================
"""

from abc import ABC, abstractmethod
import requests
from requests import Response
import json
# from card_manager.models import Card, Deck


class WordNotFoundError(Exception):
    def __init__(self, word):
        self.word = word
        super().__init__(
            f"Data not available for word {word}. Are you sure you spelled '{word}' correctly?"
        )

class BaseWordDataFetcher(ABC):
    """Interface for DataGetter class. DataGetter must have get_data method."""

    @abstractmethod
    def get_data(self, word: str, api_url: str) -> Response: ...


class WordDataFetcher(BaseWordDataFetcher):
    """
    Concrete class that requests data from dictionaryapi.dev.
    Returns response that contains word definitions, examples and transcription.

    Preconditions: 
    => The word is a string.
    => api_url is a string.
    """

    def get_data(self, word: str, api_url: str) -> Response:
        endpoint_url = f"{api_url}{word}"
        response = requests.get(endpoint_url, timeout=None)

        # remove this 2 lines for prod
        parsed_data = json.dumps(response.json(), indent=4, sort_keys=True)
        print(parsed_data)

        if response.status_code == 404:
            raise WordNotFoundError(word)

        return response


DICTIONARYAPI_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"
data_fetcher= WordDataFetcher()
data_fetcher.get_data("cat", DICTIONARYAPI_URL)


# def save_data(response, deck_name, user):  # this function does 2 things: process and save data
#     """
#     This function processes and saves data.
#     It can do processing and leave saving data to a view, for example.
#     """
#
#     deck, _ = Deck.objects.get_or_create(user=user, deck_name=deck_name)
#
#     # Process data to remove redundant meanings and examples
#     entry = response[0]
#
#     word = entry.get("word", "")
#     phonetic = entry.get("phonetic", "")
#     definitions = []
#     examples = []
#
#     #  this block is a little hard to read. Can be more pythonic
#     for meaning in entry.get("meanings", []):
#         for definition_obj in meaning.get("definitions", []):
#             if len(definitions) < 2:
#                 definitions.append(definition_obj.get("definition", ""))
#
#             example = definition_obj.get("example")
#             if example and len(examples) < 2:
#                 examples.append(example)
#
#             if len(definitions) >= 2 and len(examples) >= 2:
#                 break
#         if len(definitions) >= 2 and len(examples) >= 2:
#             break
#
#     cleaned_data = {
#         "word": word,
#         "phonetic": phonetic,
#         "definitions": definitions,
#         "examples": examples,
#     }
#
#     Card.objects.create(
#         deck=deck,
#         json_data=cleaned_data,
#         word=word,
#     )
#     return word if word else "success"  # return strings?


# def get_and_save(input_word, deck_name, user):
#
#     try:
#         response = get_data(input_word)
#         return save_data(response.json(), deck_name, user)
#     except WordNotFoundError as e:
#         return str(e)  # raise error and leave it to handle at the correct lvl of abstraction
