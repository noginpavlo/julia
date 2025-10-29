"""
This module handles algoryttmic calculations needed for SM2 cards scheduling.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypedDict


class OutOfRangeError(ValueError):
    """Raises an error when SM2Config values are out of reasonable range."""

    def __init__(self, param: str, value: float, min_val: float, max_val: float) -> None:
        message = (
            f"Invalid value for {param}: {value}."
            f"Expected value should be in {min_val} - {max_val} range."
        )

        super().__init__(message)
        self.param = param
        self.value = value
        self.min_val = min_val
        self.max_val = max_val


class SchedulingData(TypedDict):
    """TypedDict for SM2 result ensuring correct return structure.

    Defines the structure returned by `SM2Scheduler.calculate_scheduling_data()`.
    """

    quality: int
    ef: float
    repetitions: int
    interval: float
    due_date: datetime


@dataclass
class SM2Config:
    """Config for the SM2 spaced repetition algorithm.

    Parameters are validated (if customized) to keep values within reasonable ranges
    derived from the original SM2 algorithm. This prevents unstable scheduling
    (e.g., negative or exploding intervals).

    Attributes:
        base_ef_increment (float): EF gain on success (range 0–1.0, default 0.1).
        quality_penalty_base (float): Base EF penalty (range 0–0.5, default 0.08).
        quality_penalty_factor (float): Scales penalty with low quality
            (range 0–0.1, default 0.02).
        max_quality (int): Maximum quality grade (range 1–10, default 5).
        min_ef (float): Minimum EF allowed (range 1.0–2.0, default 1.3).

    Raises:
        OutOfRangeError: If any parameter is outside its range.
    """

    base_ef_increment: float = 0.1
    quality_penalty_base: float = 0.08
    quality_penalty_factor: float = 0.02
    max_quality: int = 5
    min_ef: float = 1.3

    def __post_init__(self) -> None:
        if not 0 < self.base_ef_increment <= 1.0:
            raise OutOfRangeError("base_ef_increment", self.base_ef_increment, 0, 1.0)
        if not 0 <= self.quality_penalty_base <= 0.5:
            raise OutOfRangeError("quality_penalty_base", self.quality_penalty_base, 0, 0.5)
        if not 0 <= self.quality_penalty_factor <= 0.1:
            raise OutOfRangeError("quality_penalty_factor", self.quality_penalty_factor, 0, 0.1)
        if not 1 <= self.max_quality <= 10:
            raise OutOfRangeError("max_quality", self.max_quality, 1, 10)
        if not 1.0 <= self.min_ef <= 2.0:
            raise OutOfRangeError("min_ef", self.min_ef, 1.0, 2.0)


# you sure you can avoid interface here?
class SM2Scheduler:
    """SM2 spaced repetition scheduler.

    Uses an `SM2Config` to calculate review intervals and easiness
    factors. Core logic is in `calculate_scheduling_data()`.
    """

    def __init__(self, config: SM2Config | None = None) -> None:

        self.config = config or SM2Config()

    def calculate_scheduling_data(
        self, repetitions: int, interval: float, ef: float, quality: int
    ) -> SchedulingData:
        """
        Pure SM2 calculation: returns updated spaced repetition data.

        Args:
            repetitions: Number of successful repetitions so far
            interval: Current interval in days
            ef: Easiness factor
            quality: User feedback (1=hard, 2=medium, 3=easy)

        Returns:
            SchedulingData dict containing updated values.
        """

        if quality < 3:
            repetitions = 0  # hardcodes values !!! make them part of config later
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
        due_date = datetime.now() + timedelta(
            days=interval_days
        )  # datetime.utcnow() or allow injection of “current time” for testing

        result: SchedulingData = {
            "quality": quality,
            "ef": ef,
            "repetitions": repetitions,
            "interval": interval,
            "due_date": due_date,
        }

        return result
