from django.urls import path
from .consumers import NotificationConsumer

websocket_urlpatterns = [ 
    path('ws/notifications/(?P<user_id>\d+)/$' , NotificationConsumer.as_asgi()), 
]