from django.contrib.auth.decorators import login_required
from card_manager.services.card_dealer import get_and_save, show_card, delete_card, delete_deck, create_deck
from django.http import HttpResponse
from django.shortcuts import render
import json


@login_required
def get_and_save_view(request):
    test_word = "rat"
    deck_name = "animals"
    result = get_and_save(test_word, deck_name, request.user)
    return HttpResponse(f"Word {result} saved successfully")

@login_required
def create_deck_view(request):
    deck_name = "animals"
    result = create_deck(deck_name, request.user)
    return HttpResponse(result)

@login_required
def delete_card_view(request):
    card_id = 1
    result = delete_card(card_id, request.user)
    return HttpResponse(result)


@login_required
def delete_deck_view(request):
    deck_id = 1
    result = delete_deck(deck_id, request.user)
    return HttpResponse(result)

@login_required
def show_card_view(request):
    deck_name = "animals"
    result = show_card(deck_name, request.user)
    return render(request, "cards/show_card.html", {"card": result})
