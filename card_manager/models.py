from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


class Deck(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='decks'
    )
    deck_name = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'decks_deck'  # This ensures the DB table is named exactly as you want

    def __str__(self):
        return f'{self.deck_name}'

class Card(models.Model):
    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name='cards'
    )
    json_data = models.JSONField()
    word = models.CharField(max_length=255, db_index=True)
    quality = models.FloatField(default=1)
    ef = models.FloatField(default=1.3)
    repetitions = models.FloatField(default=0.0)
    interval = models.FloatField(default=1)
    due_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'cards_card'  # Overwrites Django’s default table naming

    def __str__(self):
        return f"{self.json_data}"

class ShowCardDailyStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "daily_card_learning"
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.count} times"