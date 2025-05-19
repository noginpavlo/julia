import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CardProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("🔌 WebSocket connect attempt")
        user = self.scope["user"]
        print("🔍 WebSocket user:", user)
        if user.is_anonymous:
            print("❌ Anonymous user — closing socket.")
            await self.close()
        else:
            self.group_name = f"user_{user.id}"
            print(f"✅ Adding to group: {self.group_name}")
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        print(f"🔌 Disconnected: {close_code}")
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def card_status(self, event):
        print(f"📨 Sending card status to client: {event['content']}")
        await self.send(text_data=json.dumps(event["content"]))
