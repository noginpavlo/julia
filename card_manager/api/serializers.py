from rest_framework import serializers
from card_manager.models import Deck, Card


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id', 'deck_name', 'date_updated']


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields= [
            'id',
            'word',
            'due_date',
        ]

