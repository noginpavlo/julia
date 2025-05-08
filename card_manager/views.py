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
def get_and_save_view(request):
    if request.method != 'POST':
        return HttpResponse("Invalid request method.", status=400)

    word = request.POST.get("word")
    deck_name = request.POST.get("deck_name")

    deck, _ = Deck.objects.get_or_create(user=request.user, deck_name=deck_name)

    if Card.objects.filter(deck=deck, json_data__word__iexact=word).exists():
        return JsonResponse(
            {"message": f"Word '{word}' already exists in your '{deck_name}' deck."},
            status=400,
        )

    try:
        result = get_and_save(word, deck_name, request.user)
    except Exception:
        return JsonResponse({"error": "Oops, something went wrong on our end."}, status=500)

    if isinstance(result, str) and result.startswith("Data not available for word"):
        return JsonResponse({"message": result}, status=400)

    return JsonResponse({"message": f"Word '{result}' saved successfully!"})


@login_required
@catch_views_errors
def delete_card_view(request):
    card_id = 1
    result = delete_card(card_id, request.user)
    return HttpResponse(result)


@login_required
@catch_views_errors
def delete_deck_view(request):
    deck_id = 1
    result = delete_deck(deck_id, request.user)
    return HttpResponse(result)


@login_required
@catch_views_errors
def show_card_view(request):
    deck_name = "animals"

    if request.method == "POST":
        card_id = request.POST.get("card_id")
        user_feedback = int(request.POST.get("user_feedback"))
        sm2(card_id, user_feedback, request.user)

        return redirect('show-card')

    result = show_card(deck_name, request.user)

    if result == "No cards left for today":
        return HttpResponse(f"Congratulations☺️ You've learned all cards in '{deck_name}' deck for today.")

    return render(request, "cards/show_card.html", {"card": result})


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

