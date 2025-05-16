from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Deck, Card
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status


@login_required
def create_card_view(request):
    return render(request, "cards/create_card.html")


@login_required
def oops_view(request):
    return render(request, "errors/oops.html")


@login_required
def show_card_template_view(request):
    return render(request, "cards/show_card.html")


@api_view(["GET"])
def deck_list(request):
    if request.user.is_authenticated:
        decks = Deck.objects.filter(user=request.user)
        deck_data = [{"id": deck.id, "deck_name": deck.deck_name} for deck in decks]
        return Response(deck_data)
    else:
        return JsonResponse(
            {"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED
        )


@login_required
def show_decks(request):
    return render(request, "deck_browser/deck_list.html")


@login_required
def show_cards(request, deck_id):
    deck = Deck.objects.get(id=deck_id, user=request.user)
    cards = Card.objects.filter(deck=deck)
    return render(
        request, "deck_browser/card_list.html", {"deck": deck, "cards": cards}
    )
