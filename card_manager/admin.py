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
            obj (Deck): The deck instance.

        Returns:
            str: HTML anchor tag linking to the list of Cards filtered by the Deck.
        """
        url = reverse("admin:card_manager_card_changelist") + f"?deck__id__exact={obj.id}"
        return format_html("<a class='button' href='{}'>View Cards</a>", url)


@admin.register(Card)
class CardAdmin(ModelAdmin):
    """Representation for the Card model in django-admin.

    Displays card, deck and user fields. Filters by deck and user.
    Provides search by word, deck and user.
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
        """Retrieve the user who owns the Deck where the Card is.

        Args:
            obj (Card): The card instance from admin list.

        Returns:
            AbstractBaseUser: The user owning the deck where the card is.
        """
        return obj.deck.user


admin.site.register(ShowCardDailyStat)  # this shows how many times user learned a card on the date
