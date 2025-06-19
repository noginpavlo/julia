import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
    AuthenticationFailed,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()


class CardProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract token from subprotocols list
        token_str = None
        for proto in self.scope.get("subprotocols", []):
            if proto.startswith("access-token."):
                token_str = proto.split("access-token.")[1]
                break

        user = AnonymousUser()
        if token_str:
            user = await self.authenticate_user_from_token(token_str)

        if user and user.is_authenticated:
            self.scope["user"] = user
            self.group_name = f"user_{user.id}"

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name,
            )
            await self.accept(subprotocol=f"access-token.{token_str}")
            print(f"✅ WebSocket connected: user {user.username}")
        else:
            print("❌ WebSocket rejected: invalid or missing token")
            await self.close()

    @staticmethod
    async def authenticate_user_from_token(token_str):
        try:
            AccessToken(token_str)

            jwt_authenticator = JWTAuthentication()
            validated_token = jwt_authenticator.get_validated_token(token_str)

            user_id = validated_token["user_id"]
            user = await sync_to_async(User.objects.get)(id=user_id)
            return user

        except (User.DoesNotExist, InvalidToken, TokenError) as e:
            print(f"❌ JWT auth failed: {e}")
            return AnonymousUser()

    async def disconnect(self, close_code):
        print(f"🔌 Disconnected with code: {close_code}")
        group = getattr(self, "group_name", None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)
            print(f"👋 Removed channel from group: {group}")
        else:
            print("⚠️ No group_name found — skipping group discard.")

    async def card_status(self, event):
        await self.send(text_data=json.dumps(event["content"]))
