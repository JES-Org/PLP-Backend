from django.urls import path
from .views import UnreadNotificationsView, MarkNotificationAsReadView

urlpatterns = [
    path('unread/', UnreadNotificationsView.as_view(), name='unread-notifications'),
    path('<int:notification_id>/mark-read/', MarkNotificationAsReadView.as_view(), name='mark-notification-read'),
]
