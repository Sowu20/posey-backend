from urllib.parse import parse_qs
from channels.middleware.base import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_params = parse_qs(scope["query_string"].decode())
        token = query_params.get("token", [None])[0]

        if token:
            try:
                validated_token = AccessToken(token)
                user = await self.get_user(validated_token["user_id"])
                scope["user"] = user
            except Exception:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @staticmethod
    async def get_user(user_id):
        try:
            return await User.objects.aget(pk=user_id)
        except User.DoesNotExist:
            return AnonymousUser()