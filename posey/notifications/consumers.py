import json 
from channels.generic.websocket import AsyncWebsocketConsumer 

class NotificationConsumer(AsyncWebsocketConsumer): 
    async def connect(self): 
        user = self.scope["user"]
        if user.is_anonymous:
            # Refuse la connexion si pas authentifié
            await self.close()
        else:
            self.group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self,close_code): 
        # Quitter le groupe de notification utilisateur 
        await self.channel_layer.group_discard( 
            self.group_name, 
            self.channel_name 
        ) 

    async def send_notification(self, event): 
        notification = event['message'] 

        # Envoyer un message à WebSocket 
        await self.send(text_data=json.dumps({ 
            'notification' : notification 
        }))