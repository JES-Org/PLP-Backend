from django.urls import path
from .views import (
    ForumMessageListCreateAPIView,
    ForumMessageUpdateAPIView,
    ForumMessageDeleteAPIView
)

urlpatterns = [
    path('<int:classroom_id>/messages', ForumMessageListCreateAPIView.as_view(), name='forum-message-list-create'),
    path('<int:classroom_id>/update-message', ForumMessageUpdateAPIView.as_view(), name='forum-message-update'),
    path('<int:classroom_id>/delete-message', ForumMessageDeleteAPIView.as_view(), name='forum-message-delete'),
]
