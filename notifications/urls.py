# urls.py
from django.urls import path
from .views import UnreadNotificationsAPIView, NotificationDetailAPIView

urlpatterns = [
    path('unread/', UnreadNotificationsAPIView.as_view(), name='unread-notifications'),
    path('<int:notification_id>/', NotificationDetailAPIView.as_view(), name='notification-detail'),
]
