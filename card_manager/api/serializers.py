from rest_framework import serializers
from card_manager.models import Deck

class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id', 'deck_name', 'date_created', 'date_updated']