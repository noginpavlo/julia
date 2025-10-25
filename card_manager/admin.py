from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from django.utils.html import format_html

from .models import Card, Deck, ShowCardDailyStat


@admin.register(Deck)
class DeckAdmin(ModelAdmin):
    """Representation for the Deck model in django-admin.

    Provides deck listing, search, and a link to view all cards
    belonging to each deck.
    """

    date_hierarchy = "date_created"
    list_display = (
        "deck_name",
        "user",
        "view_cards_link",
    )
    search_fields = (
        "deck_name",
        "user__username",
    )

    @admin.display(description="cards")
    def view_cards_link(self, obj: Deck) -> str:
        """Generate a clickable link to view all cards for this deck.

        Args:
            obj (Deck): The deck instance being displayed in the admin list.

        Returns:
            str: HTML anchor element linking to the Card changelist filtered by this deck.
        """
        url = reverse("admin:card_manager_card_changelist") + f"?deck__id__exact={obj.id}"
        return format_html("<a class='button' href='{}'>View Cards</a>", url)


@admin.register(Card)
class CardAdmin(ModelAdmin):
    """Representation for the Card model in django-admin.

    Displays card fields, filters by deck and user, and provides
    the user column derived from the related Deck model.
    """

    date_hierarchy = "due_date"
    list_display = (
        "word",
        "deck",
        "get_user",
    )
    list_filter = (
        "deck",
        "deck__user",
    )
    search_fields = (
        "word",
        "deck__deck_name",
        "deck__user__username",
    )

    @admin.display(description="user", ordering="deck__user")
    def get_user(self, obj: Card) -> AbstractBaseUser:
        """Retrieve the user associated with this card via its deck.

        Args:
            obj (Card): The card instance being displayed in the admin list.

        Returns:
            AbstractBaseUser: The user owning the deck that contains this card.
        """
        return obj.deck.user


admin.site.register(ShowCardDailyStat)  # this shows how many times user learned a card on the date
