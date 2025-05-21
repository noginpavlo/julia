from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    DeckSerializer,
    CardSerializer,
    CardCreateSerializer,
    ShowCardSerializer,
    CardUpdateSerializer,
)
from .pagination import CustomPageNumberPagination
from card_manager.models import Deck, Card
from django.shortcuts import get_object_or_404
from card_manager.services.card_dealer import sm2, show_card


class DeckListView(ListAPIView):
    serializer_class = DeckSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        deck_queryset = Deck.objects.filter(user=self.request.user).order_by(
            "-date_updated"
        )

        search_query = self.request.GET.get("search", "")
        if search_query:
            deck_queryset = deck_queryset.filter(deck_name__istartswith=search_query)

        return deck_queryset


class CardListByDeckView(ListAPIView):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        deck_id = self.kwargs["deck_id"]
        card_queryset = Card.objects.filter(
            deck__id=deck_id, deck__user=self.request.user
        ).order_by("due_date")

        search_query = self.request.GET.get("search", "")
        if search_query:
            card_queryset = card_queryset.filter(word__istartswith=search_query)

        return card_queryset


class CardCreateView(CreateAPIView):
    serializer_class = CardCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        word = serializer.validated_data["word"]
        deck_name = serializer.validated_data["deck_name"]

        deck, _ = Deck.objects.get_or_create(user=request.user, deck_name=deck_name)

        if Card.objects.filter(deck=deck, json_data__word__iexact=word).exists():
            return Response(
                {
                    "message": f"Word '{word}' already exists in your '{deck_name}' deck."
                },
                status=400,
            )

        try:
            result = (
                serializer.save()
            )  # calls serializer.create(serializer.validated_data)
        except Exception:
            return Response(
                {"error": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": f"Card for '{result}' is being created. This may take a moment."
            },
            status=status.HTTP_202_ACCEPTED,  # 202 = Accepted for processing
        )


class CardDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(deck__user=self.request.user)

    def delete(self, request, *args, **kwargs):
        card_id = kwargs.get("pk")
        card = get_object_or_404(Card, id=card_id, deck__user=request.user)
        card.delete()

        return Response(
            {"message": "Card deleted successfully."}, status=status.HTTP_204_NO_CONTENT
        )


class DeckDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Deck.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        deck_id = kwargs.get("pk")
        deck = get_object_or_404(Deck, id=deck_id, user=request.user)
        deck.delete()  # deletes the deck and all cards in deck (CASCADE)

        return Response(
            {"message": "Deck and all its cards deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


# is this function redundant after using Celery task in tasks.py???
class ShowCardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    deck_name = "animals"  # NOTE THAT THIS IS HARDCODED FOR TESTING

    def get(self, request):
        result = show_card(self.deck_name, request.user)

        if result == "No cards left for today":
            return Response(
                {
                    "message": f"Congratulations☺️ You've learned all cards in '{self.deck_name}' deck for today."
                },
                status=status.HTTP_200_OK,
            )

        serializer = ShowCardSerializer(result)
        return Response(serializer.data)

    def post(self, request):
        card_id = request.data.get("card_id")
        user_feedback = request.data.get("user_feedback")

        if not card_id or not user_feedback:
            return Response(
                {"error": "Missing card_id or user_feedback."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_feedback = int(user_feedback)
            sm2(card_id, user_feedback, request.user)
        except Exception as e:
            return Response(
                {"error": "Failed to update card."}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Card updated successfully."}, status=status.HTTP_200_OK
        )


class CardUpdateView(UpdateAPIView):
    serializer_class = CardUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(deck__user=self.request.user)

    def patch(self, request, *args, **kwargs):
        card = self.get_object()
        serializer = CardUpdateSerializer(card, data=request.data, partial=True)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response({"status": "updated"}, status=200)
