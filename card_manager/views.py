from django.contrib.auth.decorators import login_required
from card_manager.services.card_dealer import (
    get_and_save, show_card, delete_card, delete_deck, sm2, update_card
    )
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Deck, Card
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status


def catch_views_errors(func):
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            return redirect("oops")
    return wrapper


@login_required
def create_card_view(request):
    return render(request, "cards/create_card.html")

@login_required
def oops_view(request):
    return render(request, "errors/oops.html")


@login_required
def show_card_template_view(request):
    return render(request, "cards/show_card.html")


# In this function later AJAX will be applied with JsonResponse so here is no @catch_views_errors
@login_required
def update_card_view(request):
    user = request.user

    if request.method == "POST":
        update_card(request, user)

    return redirect('show-card')


@api_view(['GET'])
def deck_list(request):
    if request.user.is_authenticated:
        decks = Deck.objects.filter(user=request.user)
        deck_data = [{"id": deck.id, "deck_name": deck.deck_name} for deck in decks]
        return Response(deck_data)
    else:
        return JsonResponse({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)


def show_decks(request):
    return render(request, 'deck_browser/deck_list.html')


def show_cards(request, deck_id):
    deck = Deck.objects.get(id=deck_id, user=request.user)
    cards = Card.objects.filter(deck=deck)
    return render(request, 'deck_browser/card_list.html', {'deck': deck, 'cards': cards})

