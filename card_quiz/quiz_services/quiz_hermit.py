from card_manager.models import Card


def get_quiz_cards(user, deck_ids):
    def fetch_cards(queryset, count):
        return list(
            queryset.order_by("?")[:count] # django docs from DOU suggest that you need to avoid order_by(?). Study why!
        )  # returns rows in random order (SQL =>ORDER BY RANDOM())

    base_qs = Card.objects.filter(deck__user=user, deck_id__in=deck_ids)

    hard_qs = base_qs.filter(ef__gte=1.3, ef__lt=2.0)
    medium_qs = base_qs.filter(ef__gte=2.0, ef__lt=3.5)
    easy_qs = base_qs.filter(ef__gte=3.5)

    hard_cards = fetch_cards(hard_qs, 6)
    medium_cards = fetch_cards(medium_qs, 8)
    easy_cards = fetch_cards(easy_qs, 6)

    for card in hard_cards:
        card.difficulty = "hard"
    for card in medium_cards:
        card.difficulty = "medium"
    for card in easy_cards:
        card.difficulty = "easy"

    combined = hard_cards + medium_cards + easy_cards

    # this section handles a case where it is not enough cards of specific category in the deck(s) scope
    total_needed = 20
    if len(combined) < total_needed:
        already_ids = [card.id for card in combined]
        remaining = total_needed - len(combined)

        fallback_qs = base_qs.exclude(id__in=already_ids)
        fallback_cards = fetch_cards(fallback_qs, remaining)
        for card in fallback_cards:
            card.difficulty = "fallback"

        combined += fallback_cards

    print(combined)
    return combined
