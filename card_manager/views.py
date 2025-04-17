from django.contrib.auth.decorators import login_required
from card_manager.services.card_dealer import save_data
from card_manager.services.card_dealer import get_and_save
from django.http import HttpResponse


def save_card_view(request):
    array = [
            "2077-04-07",
             "blade",
             "blaid",
             "Something that bladerunner runns on",
             "Oh, you thought it is you, Bladerunner...",
             1
            ]
    result = save_data(array)
    return HttpResponse(result)

@login_required
def get_and_save_view(request):
    test_word = "novel"
    result = get_and_save(test_word, request.user)
    return HttpResponse(result)