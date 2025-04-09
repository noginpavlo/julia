# from django.shortcuts import render
from card_manager.services.card_dealer import save_data
from django.http import HttpResponse


def save_card_view(request):
    array = ["2025-04-07", "newdatat", "something here", "test", "Let's be so programatic about it", 1]
    result = save_data(array)
    return HttpResponse(result)