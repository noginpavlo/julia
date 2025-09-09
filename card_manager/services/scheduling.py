from datetime import datetime, timedelta
from typing import TypedDict


class SchedulingData(TypedDict):

    quality: int
    ef: float
    repetitions: int
    interval: float
    due_date: datetime


class SM2Config:

    def __init__(
        self,
        base_ef_increment: float = 0.1,
        quality_penalty_base: float = 0.08,
        quality_penalty_factor: float = 0.02,
        max_quality: int = 5,
        min_ef: float = 1.3,
    ) -> None:

        self._base_ef_increment = base_ef_increment
        self._quality_penalty_base = quality_penalty_base
        self._quality_penalty_factor = quality_penalty_factor
        self._max_quality = max_quality
        self._min_ef = min_ef


class SM2Scheduler:

    def __init__(self, config: SM2Config = None) -> None:

        self.config = config or SM2Config()

    def calculate_scheduling_data(
        self, repetitions: int, interval: float, ef: float, quality: int
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

        penalty = (self.config.max_quality - quality) * (
            self.config.quality_penalty_base
            + (self.config.max_quality - quality) * self.config.quality_penalty_factor
        )
        new_ef = ef + self.config.base_ef_increment - penalty
        ef = max(new_ef, self.config.min_ef)
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
