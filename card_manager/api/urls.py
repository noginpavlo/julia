from django.urls import path
from .views import DeckListView, CardListByDeckView

urlpatterns = [
    path('decks/', DeckListView.as_view(), name='deck-list'),
    path('decks/<int:deck_id>/cards/', CardListByDeckView.as_view(), name='deck-cards'),
]