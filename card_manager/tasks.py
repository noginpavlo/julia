"""
This module is convoluted and hard to read. Redesign it. Use OOP and adhere to SRP. 
"""
import logging
import socket
import traceback

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

from card_manager.services.card_dealer import get_and_save

logger = logging.getLogger(__name__)


# consider using OOP here
@shared_task(bind=True)
def create_card_task(
    self, word, deck_name, user_id
):  # redesign this function completely.

    user_model = get_user_model()
    channel_layer = get_channel_layer()

    try:
        socket.create_connection(("localhost", 6379), timeout=2)
    except Exception as e:  # too generic exception
        logger.warning(
            "❌ Redis is NOT reachable from Celery: %s(message from #card_manager/tasks.py, create_card_task)",
            e,
        )

    try:
        user = user_model.objects.get(id=user_id)
        result = get_and_save(
            word, deck_name, user
        )  # the frontend notifications depend on what this line returns

        if isinstance(result, str) and result.startswith("Data not available for word"):
            message = {
                "status": "error",
                "type": "word_not_found",
                "message": result,
            }
        elif isinstance(result, str) and result.startswith("Word already in the deck"):
            message = {
                "status": "error",
                "type": "card_exists",
                "message": result,
            }
        else:
            message = {
                "status": "success",
                "type": "card_created",
                "message": f"Card for '{result}' created.",
            }

        logger.info(
            "📤 Sending WebSocket message: %s(message from #card_manager/tasks.py, create_card_task)",
            message,
        )

        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{user_id}",
                {
                    "type": "card_status",
                    "content": message,
                },
            )
            logger.info("✅ Message sent to channel layer.")
        else:
            logger.warning("⚠️ Cannot send WebSocket message: channel_layer is None")

        return message

    except Exception as e:  # too general exception
        logger.error("❌ Exception in create_card_task:")
        traceback.print_exc()

        error_msg = {
            "status": "error",
            "type": "exception",
            "message": str(e),
        }

        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"user_{user_id}",
                    {
                        "type": "card_status",
                        "content": error_msg,
                    },
                )
                logger.info(
                    "✅ Error message sent to channel layer.(message from #card_manager/tasks.py, create_card_task)"
                )
            except Exception:  # too general exception
                logger.error(
                    "❌ Failed to send error message via WebSocket:(message from #card_manager/tasks.py, create_card_task)"
                )
                traceback.print_exc()
        else:
            logger.warning(
                "⚠️ Cannot send error WebSocket message: channel_layer is None(message from #card_manager/tasks.py, create_card_task)"
            )

        return error_msg
