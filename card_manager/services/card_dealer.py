"""
THIS MODULE IS REDUNDATN
"""
import random
import os
import sys

import django
import requests
from card_manager.models import Card, Deck, ShowCardDailyStat

# Set the default settings module for Django and initialize Django
# (needed for standalone scripts that interact with django)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "julia.settings")
django.setup()


class WordNotFoundError(Exception):
    def __init__(self, word):
        self.word = word
        super().__init__(
            f"Data not available for word {word}. Are you sure you spelled '{word}' correctly?"
        )


def log_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:  # too generic exception
            print(f"Unexpected error in {func.__name__}: {e}")  # logger
            raise

    return wrapper


@log_errors
def get_data(input_word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{input_word}"  # hardcoded url
    response = requests.get(url)

    if response.status_code == 404:
        raise WordNotFoundError(input_word)

    return response


@log_errors
def save_data(response, deck_name, user):  # this function does 2 things: process and save data
    """
    This function processes and saves data.
    It can do processing and leave saving data to a view, for example.
    """

    deck, created = Deck.objects.get_or_create(user=user, deck_name=deck_name)

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


@log_errors
def get_and_save(input_word, deck_name, user):

    try:
        response = get_data(input_word)
        return save_data(response.json(), deck_name, user)
    except WordNotFoundError as e:
        return str(e)  # raise error and leave it to handle at the correct lvl of abstraction


@log_errors
def create_deck(deck_name, user):
    # this might be redundant
    # why this is not handled by view? Pause on this and figure out
    Deck.objects.get_or_create(user=user, deck_name=deck_name)
    return f"Deck {deck_name} created"


@log_errors
def delete_card(card_id, user):
    # this might be redundant

    card_to_delete = Card.objects.get(id=card_id, deck__user=user)
    card_to_delete.delete()
    return f"Card id {card_id} deleted successfully"


@log_errors
def delete_deck(deck_id, user):
    # this might be redundant
    # view?

    deck_to_delete = Deck.objects.get(id=deck_id, user=user)
    deck_to_delete.delete()
    return f"Deck id {deck_id} deleted successfully"


@log_errors
def show_card(deck_name, user):
    # again this just retrieves the card from the database. View?

    # can this function be called from view? and here remove show card at all?
    increment_daily_learning(user)

    now = timezone.now()

    all_cards_ids = list(
        Card.objects.filter(
            deck__deck_name=deck_name,
            deck__user=user,
            due_date__lte=now,  # __lte stands for 'less than or equal to'
        ).values_list("id", flat=True)
    )

    if not all_cards_ids:
        return "No cards left for today"

    card_id = random.choice(all_cards_ids)
    card_to_show = Card.objects.get(id=card_id, deck__user=user)

    return card_to_show


@log_errors
def increment_daily_learning(user):  # this is related to data collected from the user not to sm2
    today = date.today()

    stat, created = ShowCardDailyStat.objects.get_or_create(user=user, date=today)

    if not created:
        stat.count = F("count") + 1
    else:
        stat.count = 1  # First time today, set count to 1

    stat.save(update_fields=["count"])
    stat.refresh_from_db()

    return stat


@log_errors
def sm2(card_id, user_feedback, user):
    """
    Does this function calculates sm2 and saves the data to the db?
    It should just calculate the parametars and return them for the caller to db-save
    """

    card = Card.objects.get(id=card_id, deck__user=user)

    card.quality = user_feedback
    card.save(update_fields=["quality"])

    if user_feedback < 3:
        Card.objects.filter(id=card.id).update(
            interval=1,
            repetitions=0,
        )
    else:
        if card.repetitions == 0:
            Card.objects.filter(id=card.id).update(interval=1, repetitions=F("repetitions") + 1)
        elif card.repetitions == 1:
            Card.objects.filter(id=card.id).update(interval=3, repetitions=F("repetitions") + 1)
        else:
            Card.objects.filter(id=card.id).update(
                interval=F("interval") * F("ef"), repetitions=F("repetitions") + 1
            )

    card.refresh_from_db(fields=["interval", "repetitions", "ef"])

    # parameters hardcoded? what if I want to change them later?
    new_ef = card.ef + (0.1 - (5 - user_feedback) * (0.08 + (5 - user_feedback) * 0.02))
    card.ef = max(new_ef, 1.3)

    interval_days = round(float(card.interval))
    card.due_date = timezone.now() + timedelta(days=interval_days)

    card.save(update_fields=["ef", "due_date"])

# ===========================================================================================
# THIS IS THE END

@log_errors
def update_card(request, user):

    card_id = request.POST.get("card_id")
    card = Card.objects.get(id=card_id, deck__user=user)

    if request.POST.get("changed") == "true":
        card_data = card.json_data

        word = request.POST.get("word", card_data.get("word", ""))
        card_data["word"] = request.POST.get("word", card_data.get("word", ""))
        card_data["phonetic"] = request.POST.get("phonetic", card_data.get("phonetic", ""))
        card_data["definitions"] = [
            request.POST.get("meaning1", ""),
            request.POST.get("meaning2", ""),
        ]
        card_data["examples"] = [
            request.POST.get("example1", ""),
            request.POST.get("example2", ""),
        ]

        card.json_data = card_data
        card.word = word

        card.save()

    return card


@log_errors
def update_data(card, updated_fields: dict):
    """
    Update a card's json_data field with selectively updated fields
    (word, phonetic, definitions, examples).
    """
    card_data = card.json_data or {}

    word = updated_fields.get("word", card_data.get("word", ""))
    phonetic = updated_fields.get("phonetic", card_data.get("phonetic", ""))

    definitions = [
        updated_fields.get("meaning1", ""),
        updated_fields.get("meaning2", ""),
    ]

    examples = [updated_fields.get("example1", ""), updated_fields.get("example2", "")]

    cleaned_data = {
        "word": word,
        "phonetic": phonetic,
        "definitions": definitions,
        "examples": examples,
    }

    card.word = word
    card.json_data = cleaned_data
    card.save()

    return "success"
