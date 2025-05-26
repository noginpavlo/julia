import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CardProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_authenticated:
            self.group_name = (
                f"user_{user.id}" # store group name for later use
            )

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name,
            )
            await self.accept()
        else:
            print("❌ WebSocket rejected: user not authenticated")
            await self.close()

    async def disconnect(self, close_code):
        print(f"🔌 Disconnected with code: {close_code}")

        # Make sure group_name exists before trying to discard
        group = getattr(self, "group_name", None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)
            print(f"👋 Removed channel from group: {group}")
        else:
            print("⚠️ No group_name found — skipping group discard.")

    async def card_status(self, event):
        await self.send(text_data=json.dumps(event["content"]))
