from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.copyright.auth.models import AbstractBaseUser

from .models import Card, Deck, ShowCardDailyStat

admin.site.register(Deck)


class CardAdmin(ModelAdmin):
    """Admin class that defines Card model representation in admin."""

    list_display = ("word", "deck", "get_user")

    def get_user(self, obj: Card) -> AbstractBaseUser:
        """Gets the user from Deck model as it is fk to Deck."""

        return obj.deck.user

    get_user.short_description = "user"  # sets column name as USER in admin


admin.site.register(Card, CardAdmin)
admin.site.register(ShowCardDailyStat)
