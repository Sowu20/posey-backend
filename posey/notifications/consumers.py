import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        user_id = int(self.scope["url_route"]["kwargs"]["user_id"])

        if user.is_authenticated and user.id == user_id:
            self.group_name = f"user_{user_id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_notification",
                "message": data.get("message", "")
            }
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))