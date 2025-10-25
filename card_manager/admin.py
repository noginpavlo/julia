from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from django.utils.html import format_html

from .models import Card, Deck, ShowCardDailyStat


@admin.register(Deck)
class DeckAdmin(ModelAdmin):
    """Admin class that defines Deck model representation in admin."""

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
    def view_cards_link(self, obj):
        url = reverse("admin:card_manager_card_changelist") + f"?deck__id__exact={obj.id}"
        return format_html("<a class='button' href='{}'>View Cards</a>", url)


@admin.register(Card)
class CardAdmin(ModelAdmin):
    """Admin class that defines Card model representation in admin."""

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
        """Gets user from Deck model (which is fk)."""
        return obj.deck.user


admin.site.register(ShowCardDailyStat)  # this shows how many times user learned a card on the date
