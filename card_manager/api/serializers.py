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

        """ 
        Curated card creation in Celery.
        """
        from card_manager.tasks import create_card_task

        create_card_task.delay(
            word, deck_name, user.id
        )  # curates card creation in Redis for Celery to pick up later
        return word


class ShowCardSerializer(ModelSerializer):
    class Meta:
        model = Card
        fields = ["id", "word", "json_data"]


class CardUpdateSerializer(ModelSerializer):
    word = CharField(write_only=True, required=False, allow_blank=True)
    phonetic = CharField(write_only=True, required=False, allow_blank=True)
    meaning1 = CharField(write_only=True, required=False, allow_blank=True)
    meaning2 = CharField(write_only=True, required=False, allow_blank=True)
    example1 = CharField(write_only=True, required=False, allow_blank=True)
    example2 = CharField(write_only=True, required=False, allow_blank=True)
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
        extra_kwargs = {"id": {"read_only": True}}

    def update(self, instance, validated_data):
        from card_manager.services.card_dealer import update_data

        if validated_data.get("changed"):
            try:
                result = update_data(instance, validated_data)
                if result != "success":
                    print(f"update_data failed: {result}")
            except Exception as e:
                print(f"Exception in update_data: {e}")

        return instance
