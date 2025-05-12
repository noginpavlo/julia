from rest_framework.serializers import Serializer, ModelSerializer, SerializerMethodField, CharField
from card_manager.models import Deck, Card


class DeckSerializer(ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id', 'deck_name', 'date_updated']


class CardSerializer(ModelSerializer):
    class Meta:
        model = Card
        fields= [
            'id',
            'word',
            'due_date',
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
    definition = SerializerMethodField()

    class Meta:
        model = Card
        fields = ['id', 'word', 'definition']

    def get_definition(self, obj):
        return obj.json_data.get("definition", "")
