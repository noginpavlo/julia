import os
import django
import sys
import requests
from card_manager.models import Card
from card_manager.models import Deck


# Set the default settings module for Django and initialize Django
# (needed for standalone scripts that interact with django)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "julia.settings")
django.setup()


def catch_errors(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            raise
    return wrapper


@catch_errors
def get_data(input_word):
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{input_word}'
    response = requests.get(url)

    # This word does not exist error
    if response.status_code == 404:
        raise ValueError(f"Data not available for the word: {input_word} (404 Error)")

    # Catching any kind of other errors related to api data retrieving
    if response.status_code != 200:
        raise ValueError(f"Unexpected error occurred with status code: {response.status_code}")

    return response, input_word


@catch_errors
def save_data(response, word, user):
    print("save_data called!")
    # Create test deck
    deck, created = Deck.objects.get_or_create(user=user, deck_name="test_deck")

    print(f"HERE IS THE UNPROCESSED DATA TO SAVE\n{response}")

    entry = response[0]

    word = entry.get("word", "")
    phonetic = entry.get("phonetic", "")
    definitions = []
    examples = []

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
        "examples": examples
    }

    print(f"HERE IS THE CLEAN DATA TO SAVE\n{cleaned_data}")

    # Create a new record in the JuliaTest table using Django ORM
    Card.objects.create(
        deck=deck,
        front=word,
        back=cleaned_data,
        e_param=123,
        m_param=22,
        h_param=324,
    )
    print(f"Successfully recorded data for word '{word}'")
    return word if word else "success"

@catch_errors
def get_and_save(input_word, user):
    response, word = get_data(input_word)
    save_result = save_data(response.json(), word, user)
    return save_result

@catch_errors
def create_deck(deck_name, user):
    deck, created = Deck.objects.get_or_create(user=user, deck_name=deck_name)
    return f"Deck {deck_name} created"

@catch_errors
def delete_card(card_id, user):
    print("delete_card triggered")

    #Initialize card object with spesified id and .delete() it
    # deck__user=user specifies that card is related to a deck that has user info. Cards don't have user inf.
    card_to_delete = Card.objects.get(id=card_id, deck__user=user)
    card_to_delete.delete()
    return f"Card id {card_id} deleted successfully"

@catch_errors
def delete_deck(deck_id, user):
    print("delete_deck() triggered")

    # init deck obj and delete if user is logged in
    deck_to_delete = Deck.objects.get(id=deck_id, user=user)
    deck_to_delete.delete()
    return f"Deck id {deck_id} deleted successfully"

