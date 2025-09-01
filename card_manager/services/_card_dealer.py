"""
This module handles busyness logic of the application.
It inclutes retrieving data from 3rd party API, processing the data.
It implements sm2 algorithm and handles the algorithmic data to highler-level of abstraction.

====================================================================================
This is a mock module dockstring, make it better as soon as you complete the module.
====================================================================================
"""

import requests
from card_anager.models import Card, Deck, ShowCardDailyStat


class WordNotFoundError(Exception):
    def __init__(self, word):
        self.word = word
        super().__init__(
            f"Data not available for word {word}. Are you sure you spelled '{word}' correctly?"
        )


def get_data(input_word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{input_word}"  # hardcoded url
    response = requests.get(url)

    if response.status_code == 404:
        raise WordNotFoundError(input_word)

    return response


def save_data(response, deck_name, user):  # this function does 2 things: process and save data
    """
    This function processes and saves data.
    It can do processing and leave saving data to a view, for example.
    """

    deck, _ = Deck.objects.get_or_create(user=user, deck_name=deck_name)

    # Process data to remove redundant meanings and examples
    entry = response[0]

    word = entry.get("word", "")
    phonetic = entry.get("phonetic", "")
    definitions = []
    examples = []

    #  this block is a little hard to read. Can be more pythonic
    for meaning in entry.get("meanings", []):
        for definition_obj in meaning.get("definitions", []):
            if len(definitions) < 2:
                definitions.append(definition_obj.get("definition", ""))

            example = definition_obj.get("example")
            if example and len(examples) < 2:
                examples.append(example)

            if len(definitions) >= 2 and len(examples) >= 2:
                break
        if len(definitions) >= 2 and len(examples) >= 2:
            break

    cleaned_data = {
        "word": word,
        "phonetic": phonetic,
        "definitions": definitions,
        "examples": examples,
    }

    Card.objects.create(
        deck=deck,
        json_data=cleaned_data,
        word=word,
    )
    return word if word else "success"  # return strings?


def get_and_save(input_word, deck_name, user):

    try:
        response = get_data(input_word)
        return save_data(response.json(), deck_name, user)
    except WordNotFoundError as e:
        return str(e)  # raise error and leave it to handle at the correct lvl of abstraction
