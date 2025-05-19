from card_manager.services.card_dealer import get_and_save
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
import traceback
import socket


@shared_task(bind=True)
def create_card_task(self, word, deck_name, user_id):
    print(
        f"🚀 Task started: create_card_task(word={word}, deck={deck_name}, user_id={user_id})"
    )

    user_model = get_user_model()
    channel_layer = get_channel_layer()

    try:
        socket.create_connection(("localhost", 6379), timeout=2)
        print("✅ Redis is reachable from Celery")
    except Exception as e:
        print("❌ Redis is NOT reachable from Celery:", e)

    # Debug channel layer
    print("📡 Channel layer:", channel_layer)

    try:
        user = user_model.objects.get(id=user_id)
        result = get_and_save(word, deck_name, user)

        if isinstance(result, str) and result.startswith("Data not available for word"):
            message = {
                "status": "error",
                "type": "word_not_found",
                "message": result,
            }
        else:
            message = {
                "status": "success",
                "type": "card_created",
                "message": f"Card for '{result}' created.",
            }

        print("📤 Sending WebSocket message:", message)

        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{user_id}",
                {
                    "type": "card_status",
                    "content": message,
                },
            )
            print("✅ Message sent to channel layer.")
        else:
            print("⚠️ Cannot send WebSocket message: channel_layer is None")

        return message

    except Exception as e:
        print("❌ Exception in create_card_task:")
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
                print("✅ Error message sent to channel layer.")
            except Exception as send_err:
                print("❌ Failed to send error message via WebSocket:")
                traceback.print_exc()
        else:
            print("⚠️ Cannot send error WebSocket message: channel_layer is None")

        return error_msg
