# utils.py
from notifications.models import Notification

def create_notification(classroom, title, message, notification_type, related_object_id):
    notification = Notification.objects.create(
        classroom=classroom,
        title=title,
        message=message,
        notification_type=notification_type,
        related_object_id=related_object_id
    )
    return notification
