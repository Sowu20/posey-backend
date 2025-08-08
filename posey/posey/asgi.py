"""
ASGI config for posey project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter 
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import posey.routing 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'posey.settings')

application = ProtocolTypeRouter({ 
    "http" : get_asgi_application(), 
    "websocket" : AuthMiddlewareStack( 
        URLRouter( 
            # Incluez vos routes WebSocket ici
            posey.routing.websocket_urlpatterns
         ) 
    ), 
})