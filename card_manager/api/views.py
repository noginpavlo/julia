from rest_framework import generics, permissions
from .serializers import DeckSerializer, CardSerializer
from .pagination import CustomPageNumberPagination
from card_manager.models import Deck, Card

class DeckListView(generics.ListAPIView):
    serializer_class = DeckSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Deck.objects.filter(user=self.request.user).order_by('-date_updated')


class CardListByDeckView(generics.ListAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        deck_id = self.kwargs['deck_id']
        return Card.objects.filter(deck__id=deck_id, deck__user=self.request.user).order_by('due_date')