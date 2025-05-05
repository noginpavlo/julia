from rest_framework import serializers
from card_manager.models import Deck, Card


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id', 'deck_name', 'date_created', 'date_updated']


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            'id',
            'word',
            'json_data',
            'due_date',
            'quality',
            'ef',
            'repetitions',
            'interval'
        ]


# class CardNameOnlySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Card
#         fields = ['id', 'word']
#
#
# class DeckNameOnlySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Deck
#         fields = ['id', 'deck_name', 'date_created', 'date_updated']