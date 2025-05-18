from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import classrooms.routing
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from urllib.parse import parse_qs
import os
from channels.db import database_sync_to_async
import forum.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
combined_websocket_urlpatterns = classrooms.routing.websocket_urlpatterns + forum.routing.websocket_urlpatterns


class JWTAuthMiddleware:
    """
    Custom middleware to authenticate JWT tokens from WebSocket connections
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token:
            jwt_auth = JWTAuthentication()
            try:
                validated_token = jwt_auth.get_validated_token(token)
                user = await database_sync_to_async(jwt_auth.get_user)(validated_token)
                scope['user'] = user
            except Exception as e:
                scope['user'] = AnonymousUser()
                print(f"JWT Authentication failed: {e}")
        else:
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            AuthMiddlewareStack(
             URLRouter(combined_websocket_urlpatterns)
            )
        )
    ),
})