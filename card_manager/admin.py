from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import AbstractBaseUser

from .models import Card, Deck, ShowCardDailyStat

admin.site.register(Deck)


class CardAdmin(ModelAdmin):
    """Admin class that defines Card model representation in admin."""

    list_display = ("word", "deck", "get_user")

    @admin.display(description="user", ordering="deck_user")
    def get_user(self, obj: Card) -> AbstractBaseUser:
        """Gets the user from Deck model as it is fk to Deck."""

        return obj.deck.user


admin.site.register(Card, CardAdmin)
admin.site.register(ShowCardDailyStat)
