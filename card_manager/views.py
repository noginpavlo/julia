# from django.shortcuts import render
from card_manager.services.card_dealer import save_data
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