from django.contrib.auth.decorators import login_required
from card_manager.services.card_dealer import get_and_save
from card_manager.services.card_dealer import delete_card
from card_manager.services.card_dealer import delete_deck
from django.http import HttpResponse


@login_required
def get_and_save_view(request):
    test_word = ""
    result = get_and_save(test_word, request.user)
    return HttpResponse(f"Word {result} saved successfully")

@login_required
def delete_card_view(request):
    card_id = 1
    result = delete_card(card_id, request.user)
    return HttpResponse(result)


@login_required
def delete_deck_view(request):
    deck_id = 2
    result = delete_deck(deck_id, request.user)
    return HttpResponse(result)