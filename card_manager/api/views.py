from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import DeckSerializer, CardSerializer, CardCreateSerializer
from rest_framework.exceptions import ValidationError
from .pagination import CustomPageNumberPagination
from card_manager.models import Deck, Card


class DeckListView(ListAPIView):
    serializer_class = DeckSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        deck_queryset = Deck.objects.filter(user=self.request.user).order_by('-date_updated')

        search_query = self.request.GET.get('search', '')
        if search_query:
            deck_queryset = deck_queryset.filter(deck_name__istartswith=search_query)

        return deck_queryset


class CardListByDeckView(ListAPIView):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        deck_id = self.kwargs['deck_id']
        card_queryset = Card.objects.filter(
            deck__id=deck_id,
            deck__user=self.request.user
        ).order_by('due_date')

        search_query = self.request.GET.get('search', '')
        if search_query:
            card_queryset = card_queryset.filter(word__istartswith=search_query)

        return card_queryset



class CardCreateView(CreateAPIView):
    serializer_class = CardCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        word = serializer.validated_data['word']
        deck_name = serializer.validated_data['deck_name']

        deck, _ = Deck.objects.get_or_create(user=request.user, deck_name=deck_name)

        if Card.objects.filter(deck=deck, json_data__word__iexact=word).exists():
            return Response(
                {"message": f"Word '{word}' already exists in your '{deck_name}' deck."},
                status=400,
            )

        try:
            result = serializer.save() # this == serializer.create(serializer.validated_data), but conventional
        except Exception:
            return Response({"error": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if isinstance(result, str) and result.startswith("Data not available for word"):
            return Response({"message": result}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"Word '{result}' saved successfully!"}, status=status.HTTP_201_CREATED)
