from django.db import models
from django.contrib.auth.models import User

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    deck_name = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'decks_deck'

    def __str__(self):
        return self.deck_name

