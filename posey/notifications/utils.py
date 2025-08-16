from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_user(user_id: int, message: str, payload: dict | None = None):
    """
    Push une notification temps réel au user_id ciblé via Channels.
    À appeler immédiatement après avoir créé/enregistré la notification en base.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_notification",
            "message": message,
            # "payload": payload or {},
        }
    )