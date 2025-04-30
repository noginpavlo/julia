from django.contrib.auth.decorators import login_required
from card_manager.services.card_dealer import (
    get_and_save, show_card, delete_card, delete_deck, create_deck, sm2, update_card
    )
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Deck, Card


@login_required
def create_card_view(request):
    return render(request, "cards/create_card.html")


@login_required
def get_and_save_view(request):
    test_word = "snail"
    deck_name = "animals"

    deck, created = Deck.objects.get_or_create(user=request.user, deck_name=deck_name)

    card_exists = Card.objects.filter(
        deck=deck,
        json_data__word__iexact=test_word
    ).exists()

    if card_exists:
        return HttpResponse(f"Word '{test_word}' already exists in your '{deck_name}' deck.")

    result = get_and_save(test_word, deck_name, request.user)

    #word do not exist error
    if "404 Error" in result:
        return HttpResponse(result)
    else:
        return HttpResponse(f"Word {result} saved successfully")


# DELETE this after you connect create_card.html to get_and_save(). Will be redundant
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

    if request.method == "POST":
        card_id = request.POST.get("card_id")
        user_feedback = int(request.POST.get("user_feedback"))
        sm2(card_id, user_feedback, request.user)

        return redirect('show-card')

    result = show_card(deck_name, request.user)

    if result == "No cards left for today":
        return HttpResponse(f"Congratulations☺️ You've learned all cards in '{deck_name}' deck for today.")

    return render(request, "cards/show_card.html", {"card": result})


def update_card_view(request):
    user = request.user

    if request.method == "POST":
        update_card(request, user)

    print("Successfully updated card")
    return redirect('show-card')
