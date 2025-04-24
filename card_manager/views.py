from django.contrib.auth.decorators import login_required
from card_manager.services.card_dealer import get_and_save, show_card, delete_card, delete_deck, create_deck, sm2
from django.http import HttpResponse
from django.shortcuts import render, redirect


@login_required
def get_and_save_view(request):
    test_word = "fish"
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

    if request.method == "POST":
        card_id = request.POST.get("card_id")
        print(f"HERE IS CARD_ID views: {card_id}")
        user_feedback = int(request.POST.get("user_feedback"))
        print(f"HERE IS USER FEEDBACK views: {user_feedback}")

        sm2(card_id, user_feedback, request.user)

        return redirect('show-card')

    result = show_card(deck_name, request.user)
    return render(request, "cards/show_card.html", {"card": result})

