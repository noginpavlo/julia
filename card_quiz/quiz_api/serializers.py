from rest_framework import serializers
from card_manager.models import Card


class QuizCardSerializer(serializers.ModelSerializer):
    difficulty = serializers.CharField()

    class Meta:
        model = Card
        fields = ["id", "word", "json_data", "difficulty"]
