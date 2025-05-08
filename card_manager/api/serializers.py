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


class CardCreateSerializer(serializers.Serializer):
    word = serializers.CharField()
    deck_name = serializers.CharField()

    def create(self, validated_data):
        user = self.context["request"].user
        word = validated_data["word"]
        deck_name = validated_data["deck_name"]

        from card_manager.services.card_dealer import get_and_save
        return get_and_save(word, deck_name, user)

