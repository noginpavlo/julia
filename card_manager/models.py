from django.db import models
from django.conf import settings

class JuliaTest(models.Model):
    date = models.TextField()
    word = models.TextField()
    phonetics = models.TextField()
    definition = models.TextField()
    example = models.TextField()
    increment = models.IntegerField()

    class Meta:
        db_table = 'julia_test'  # Explicitly define the table name

    def __str__(self):
        return self.word

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
    front = models.TextField()
    back = models.JSONField()
    e_param = models.FloatField(default=0.0)
    m_param = models.FloatField(default=0.0)
    h_param = models.FloatField(default=0.0)

    class Meta:
        db_table = 'cards_card'  # Overwrites Django’s default table naming

    def __str__(self):
        return self.front
