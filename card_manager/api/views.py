from rest_framework import generics, permissions
from .serializers import DeckSerializer, CardSerializer
from .pagination import CustomPageNumberPagination
from card_manager.models import Deck, Card


class DeckListView(generics.ListAPIView):
    serializer_class = DeckSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        deck_queryset = Deck.objects.filter(user=self.request.user).order_by('-date_updated')

        search_query = self.request.GET.get('search', '')
        if search_query:
            deck_queryset = deck_queryset.filter(deck_name__istartswith=search_query)

        return deck_queryset


class CardListByDeckView(generics.ListAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
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