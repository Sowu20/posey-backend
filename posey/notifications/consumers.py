import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            # Refuse la connexion si non authentifié
            await self.close()
            return

        self.group_name = f"user_{user.id}"

        # Rejoindre le groupe notifications de l'utilisateur
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Quitter le groupe notifications
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        notification = event['message']

        # Envoyer la notification au client WebSocket
        await self.send(text_data=json.dumps({
            'notification': notification
        }))