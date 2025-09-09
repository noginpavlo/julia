import django

from card_manager.models import Card

# Set the default settings module for Django and initialize Django
# (needed for standalone scripts that interact with django)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "julia.settings")
django.setup()


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
