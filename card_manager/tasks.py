from celery import shared_task
from card_manager.services.card_dealer import get_and_save
from django.contrib.auth import get_user_model


@shared_task(bind=True)
def create_card_task(
    self, word, deck_name, user_id
):  # keep self for self.retry() later
    user_model = get_user_model()

    try:
        user = user_model.objects.get(id=user_id)
        result = get_and_save(word, deck_name, user)

        # WordNotFoundError returns a message string
        if isinstance(result, str) and result.startswith("Data not available for word"):
            return {"status": "error", "type": "word_not_found", "message": result}

        return {"status": "success", "message": f"Card for '{result}' created."}

    except Exception as e:
        return {"status": "error", "type": "unknown", "message": str(e)}
