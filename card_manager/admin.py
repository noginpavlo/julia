from django.contrib import admin
from .models import Deck, Card, ShowCardDailyStat

admin.site.register(Deck)
admin.site.register(Card)
admin.site.register(ShowCardDailyStat)
