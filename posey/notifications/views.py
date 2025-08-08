from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_user(user_id, message):
    """
    Envoie une notification à un utilisateur spécifique via WebSocket.
    
    :param user_id: ID de l'utilisateur à qui envoyer la notification.
    :param message: Le message de notification à envoyer.
    """
    channel_layer = get_channel_layer()
    group_name = f"user_{user_id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',
            'message': message
        }
    )