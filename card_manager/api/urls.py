from django.urls import path
from .views import DeckListView, CardListByDeckView, CardCreateView, CardDeleteView, DeckDeleteView


urlpatterns = [
    path("decks/", DeckListView.as_view(), name="deck-list"),
    path("decks/<int:deck_id>/cards/", CardListByDeckView.as_view(), name="deck-cards"),
    path("cards/", CardCreateView.as_view(), name="create-cards"),
    path("cards/<int:pk>/", CardDeleteView.as_view(), name="delete-cards"),
    path("decks/<int:pk>/", DeckDeleteView.as_view(), name="delete-decks"),

]