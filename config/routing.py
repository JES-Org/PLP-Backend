from django.urls import re_path
from classrooms import consumers

websocket_urlpatterns = [
    re_path(r"ws/notificationhub/$", consumers.NotificationConsumer.as_asgi()),
    #re_path(r"ws/forumhub/$", consumers.ForumConsumer.as_asgi()),  # Similarly for Forum
]
