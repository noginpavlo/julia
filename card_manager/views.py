from django.contrib.auth.decorators import login_required
from card_manager.services.card_dealer import get_and_save
from card_manager.services.card_dealer import delete_card
from django.http import HttpResponse


@login_required
def get_and_save_view(request):
    test_word = "novel"
    result = get_and_save(test_word, request.user)
    return HttpResponse(result)

@login_required
def delete_card_view(request):
    card_id = 1
    result = delete_card(card_id, request.user)
    return HttpResponse(result)

