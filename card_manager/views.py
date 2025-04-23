from django.contrib.auth.decorators import login_required
from card_manager.services.card_dealer import get_and_save, show_card, delete_card, delete_deck, create_deck
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import F
from django.utils import timezone
from datetime import timedelta

@login_required
def get_and_save_view(request):
    test_word = "snail"
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

@login_required
def sm2(card, user_feedback):

    if not 0 <= user_feedback <= 5:
        raise ValueError("Feedback must be between 0 and 5.")

    card.quality = user_feedback
    repetitions = card.repetitions
    ef = card.ef

    if user_feedback < 3:
        card.repetitions = 0
        card.interval = 1
    else:
        if repetitions == 0:
            card.interval = 1
        elif repetitions == 1:
            card.interval = 3
        else:
            card.interval = F('interval') * F('ef')

        card.interval = F('interval') + 1

    new_ef = ef + (0.1 - (5 - user_feedback) * (0.08 + (5 - user_feedback) * 0.02))
    card.ef = max(new_ef, 1.3)

    card.due_date = timezone.now() + timedelta(days=card.interval)

    card.save(update_fields=['quality', 'repetitions', 'interval', 'ef', 'due_date'])
