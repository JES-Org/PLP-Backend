from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
           re_path(r"ws/chat/classroom/(?P<classroom_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
    ]
