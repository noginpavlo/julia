import os
import random
import django
import sys
import requests
from datetime import date
from django.db.models import F
from card_manager.models import Card, Deck, ShowCardDailyStat


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

    return response


@catch_errors
def save_data(response, deck_name, user):
    print("save_data called!")
    # Create test deck
    deck, created = Deck.objects.get_or_create(user=user, deck_name=deck_name)

    # Process data to remove redundant meanings and examples
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


    #Record cleaned data to cards_card table
    Card.objects.create(
        deck=deck,
        json_data=cleaned_data,
    )
    print(f"Successfully recorded data for word '{word}'")
    return word if word else "success"

@catch_errors
def get_and_save(input_word, deck_name, user):
    response = get_data(input_word)
    save_result = save_data(response.json(), deck_name, user)
    return save_result

@catch_errors
def create_deck(deck_name, user):
    deck, created = Deck.objects.get_or_create(user=user, deck_name=deck_name)
    return f"Deck {deck_name} created"

@catch_errors
def delete_card(card_id, user):
    print("delete_card triggered")

    #Initialize card object with specified id and .delete() it
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


# This function shows the whole card including front and back. Handle showing a part of it on frontend
# !!! Frontend will receive the whole card but will show only front then after click will show back
@catch_errors
def show_card(deck_name, user):

    #this function counts words learned by user every dat and saves the data to db
    increment_daily_learning(user)

    all_cards_ids = list(
        Card.objects.filter(deck__deck_name=deck_name, deck__user=user).values_list('id', flat=True)
    )

    if not all_cards_ids:
        raise ValueError(f"No cards found in deck '{deck_name}' for user '{user.username}'.")

    card_id = random.choice(all_cards_ids)
    card_to_show = Card.objects.get(id=card_id, deck__user=user)

    return card_to_show


def increment_daily_learning(user):
    today = date.today()

    stat, created = ShowCardDailyStat.objects.get_or_create(user=user, date=today)

    if not created:
        stat.count = F('count') + 1
    else:
        stat.count = 1  # First time today, set count to 1

    stat.save(update_fields=["count"])
    stat.refresh_from_db()

    print(stat)

    return stat

