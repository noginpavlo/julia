from card_manager.models import Card


def get_quiz_cards(user, deck_ids):

    """Sample cards goal is to make conditional card selection and shuffling inside the DB and not in memory"""
    def sample_cards(queryset, count, difficulty_label):
        selected = list(
            queryset.order_by("?")[:count]
        )  # returns rows in random order (SQL =>ORDER BY RANDOM())
        for card in selected:
            card.difficulty = difficulty_label
        return selected

    base_qs = Card.objects.filter(deck__user=user, deck_id__in=deck_ids)

    hard_qs = base_qs.filter(ef__gte=1.3, ef__lt=2.0)
    medium_qs = base_qs.filter(ef__gte=2.0, ef__lt=3.5)
    easy_qs = base_qs.filter(ef__gte=3.5)

    hard_cards = sample_cards(hard_qs, 6, "hard")
    medium_cards = sample_cards(medium_qs, 8, "medium")
    easy_cards = sample_cards(easy_qs, 6, "easy")

    combined = hard_cards + medium_cards + easy_cards
    print(combined)
    return combined
