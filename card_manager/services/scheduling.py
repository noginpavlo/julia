import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import TypedDict

import django

from card_manager.models import Card

# Set the default settings module for Django and initialize Django
# (needed for standalone scripts that interact with django)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "julia.settings")
django.setup()


# sm2 constants
BASE_EF_INCREMENT = 0.1
QUALITY_PENALTY_BASE = 0.08
QUALITY_PENALTY_FACTOR = 0.02
MAX_QUALITY = 5
MIN_EF = 1.3


class SchedulingData(TypedDict):

    quality: int
    ef: float
    repetitions: int
    interval: float
    due_date: datetime


class BaseScheduler(ABC):

    @staticmethod
    @abstractmethod
    def calculate_scheduling_data(
        repetitions: int, interval: float, ef: float, quality: int
    ) -> SchedulingData: ...


class SM2Scheduler(BaseScheduler):

    @staticmethod
    def calculate_scheduling_data(
        repetitions: int, interval: float, ef: float, quality: int
    ) -> SchedulingData:
        """
        Pure SM2 calculation: returns updated spaced repetition data
        without touching the database.

        Args:
            repetitions: Number of successful repetitions so far
            interval: Current interval in days
            ef: Easiness factor
            quality: User feedback (1=hard, 2=medium, 3=easy)

        Returns:
            SchedulingData dict containing updated values
        """

        if quality < 3:
            repetitions = 0
            interval = 1
        else:
            if repetitions == 0:
                interval = 1
                repetitions += 1
            elif repetitions == 1:
                interval = 3
                repetitions += 1
            else:
                interval = interval * ef
                repetitions += 1

        new_ef = ef + (
            BASE_EF_INCREMENT
            - (MAX_QUALITY - quality)
            * (QUALITY_PENALTY_BASE + (MAX_QUALITY - quality) * QUALITY_PENALTY_FACTOR)
        )
        ef = max(new_ef, MIN_EF)

        interval_days = round(interval)
        due_date = datetime.now() + timedelta(days=interval_days)

        result: SchedulingData = {
            "quality": quality,
            "ef": ef,
            "repetitions": repetitions,
            "interval": interval,
            "due_date": due_date,
        }

        return result


def sm2(card_id, user_feedback, user):
    """
    Does this function calculates sm2 and saves the data to the db?
    It should just calculate the parametars and return them for the caller to db-save
    """

    card = Card.objects.get(id=card_id, deck__user=user)

    card.quality = user_feedback  # quality corresponds to digit values easy medium hard 1,2,3
    # make a dict of relateions between quality and the number for robustness
    card.save(update_fields=["quality"])  # do it in view that updates something like this

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
