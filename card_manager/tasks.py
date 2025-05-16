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
        return {"status": "success", "message": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
