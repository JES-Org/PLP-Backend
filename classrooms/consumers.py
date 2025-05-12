import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from users.models import User
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract token from query params (or headers)
        token = self.scope.get("query_string").decode().split("=")[1]
        
        # Authenticate user via JWT
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            self.user = await sync_to_async(User.objects.get)(id=user_id)
            await self.accept()  # Accept connection if authenticated
            await self.channel_layer.group_add(f"user_{user_id}", self.channel_name)
        except Exception as e:
            print(f"Authentication failed: {e}")
            await self.close()  # Reject connection if invalid

    async def disconnect(self, close_code):
        if hasattr(self, "user"):
            await self.channel_layer.group_discard(
                f"user_{self.user.id}", self.channel_name
            )

    async def send_notification(self, event):
        # Send a real-time notification to the client
        await self.send(text_data=json.dumps(event["data"]))
