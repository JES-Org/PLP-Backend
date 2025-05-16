from notifications.models import Notification

def create_announcement_notification(announcement, sender):
    recipients = announcement.class_room.get_all_student()
    print("recipients",recipients)
    for student in recipients:
        Notification.objects.create(
            recipient=student.user,
            sender=sender,
            message=f"New announcement in {announcement.class_room.name}: {announcement.title}",
            url=f"/student/classroom/{announcement.class_room.id}/announcement"
        )
