from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from card_manager.models import Deck
from card_quiz.quiz_services.quiz_hermit import get_quiz_cards

from .serializers import QuizCardSerializer


class QuizCardsAPIView(APIView):
    # add docstring
    permission_classes = [IsAuthenticated]

    def get(self, request):  # type hints
        user = request.user
        deck_ids = request.query_params.getlist("deck_ids")

        if not deck_ids:
            return Response({"error": "deck_ids parameter is required."}, status=400)

        try:  # this might not be necessary
            deck_ids = [int(d) for d in deck_ids]
        except ValueError:
            return Response({"error": "deck_ids must be integers."}, status=400)

        # this might not be necessary
        # validated the ownership of the decks before calling quiz_services/quiz_hermit.py (get_quiz_cards)
        user_decks = Deck.objects.filter(user=user, id__in=deck_ids).values_list("id", flat=True)
        if not user_decks:
            return Response({"error": "No valid decks found for user."}, status=404)

        cards = get_quiz_cards(user, list(user_decks))
        serializer = QuizCardSerializer(cards, many=True)
        return Response(serializer.data)
