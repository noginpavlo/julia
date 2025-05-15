from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    CharField,
    BooleanField,
)
from card_manager.models import Deck, Card


class DeckSerializer(ModelSerializer):
    class Meta:
        model = Deck
        fields = ["id", "deck_name", "date_updated"]


class CardSerializer(ModelSerializer):
    class Meta:
        model = Card
        fields = [
            "id",
            "word",
            "due_date",
        ]


class CardCreateSerializer(Serializer):
    word = CharField()
    deck_name = CharField()

    def create(self, validated_data):
        user = self.context["request"].user
        word = validated_data["word"]
        deck_name = validated_data["deck_name"]

        from card_manager.services.card_dealer import get_and_save

        return get_and_save(word, deck_name, user)


class ShowCardSerializer(ModelSerializer):
    class Meta:
        model = Card
        fields = ["id", "word", "json_data"]


class CardUpdateSerializer(ModelSerializer):
    meaning1 = CharField(write_only=True, required=False)
    meaning2 = CharField(write_only=True, required=False)
    example1 = CharField(write_only=True, required=False)
    example2 = CharField(write_only=True, required=False)
    changed = BooleanField(write_only=True, required=False)

    class Meta:
        model = Card
        fields = [
            "id",
            "word",
            "phonetic",
            "meaning1",
            "meaning2",
            "example1",
            "example2",
            "changed",
        ]

    def update(self, instance, validated_data):
        if validated_data.get("changed"):
            card_data = instance.json_data

            word = validated_data.get("word", card_data.get("word", ""))
            card_data["word"] = word
            card_data["phonetic"] = validated_data.get(
                "phonetic", card_data.get("phonetic", "")
            )
            card_data["definitions"] = [
                validated_data.get("meaning1", ""),
                validated_data.get("meaning2", ""),
            ]
            card_data["examples"] = [
                validated_data.get("example1", ""),
                validated_data.get("example2", ""),
            ]

            instance.json_data = card_data
            instance.word = word

            instance.save()

        return instance
