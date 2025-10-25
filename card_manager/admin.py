from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import AbstractBaseUser

from .models import Card, Deck, ShowCardDailyStat


@admin.register(Deck)
class DeckAdmin(ModelAdmin):
    """Admin class that defines Deck model representation in admin."""

    date_hierarchy = "date_created"
    list_display = (
        "deck_name",
        "user",
    )
    search_fields = (
        "deck_name",
        "user__username",
    )


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
