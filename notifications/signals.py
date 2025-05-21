# notifications/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import Notification
from classrooms.models import Announcement,Classroom,Attachment 
from django.contrib.auth import get_user_model
from assessments.models import Assessment,Submission
from forum.models import ForumMessage
User = get_user_model()
@receiver(post_save, sender=Announcement)
def create_announcement_notification(sender, instance, created, **kwargs):
    if created:
        classroom=instance.class_room
        sender_user=classroom.teacher.user
        notification = Notification.objects.create(
            sender=sender_user,  
            message=f"New announcement in {instance.class_room.name}: {instance.title}",
            url=f"/student/classroom/{instance.class_room.id}/announcement"
        )
        recipients = classroom.get_all_student().values_list('user', flat=True)
        notification.recipients.add(*recipients)

@receiver(post_save, sender=Classroom)
def create_classroom_notification(sender,instance,created,**kwargs):
    if created:
        sender_user=instance.teacher.user
        notification = Notification.objects.create(
        sender=sender_user,  
        message=f"New classroom : {instance.name} created",
        url=f"/student/classroom/classroom-list"
          )
    recipients = instance.get_all_student().values_list('user', flat=True)
    notification.recipients.add(*recipients)
@receiver(post_save, sender=Attachment)
def create_attachment_notification(sender,instance,created,**kwargs):
    if created:
        announcement=instance.announcement
        classroom=announcement.class_room
        sender_user=classroom.teacher.user
        notification = Notification.objects.create(
        sender=sender_user,  
        message=f"New Attachment in {announcement.title} is added",
        url=f"/student/classroom/{classroom.id}/announcement"
          )
    recipients = classroom.get_all_student().values_list('user', flat=True)
    notification.recipients.add(*recipients)
@receiver(post_save, sender=Assessment)
def notify_on_assessment_publish(sender, instance, created, **kwargs):
    if created and instance.is_published:
        classroom = instance.classroom
        sender_user = classroom.teacher.user
        notification = Notification.objects.create(
            sender=sender_user,
            message=f"New assessment published in {classroom.name}: {instance.name}",
            url=f"/student/classroom/{classroom.id}/assessment"
        )
        recipients = classroom.get_all_student().values_list('user', flat=True)
        notification.recipients.add(*recipients)

    # If updated and just now published (was unpublished before)
    elif not created:
        old_instance = Assessment.objects.get(pk=instance.pk)
        if not old_instance.is_published and instance.is_published:
            classroom = instance.classroom
            sender_user = classroom.teacher.user
            notification = Notification.objects.create(
                sender=sender_user,
                message=f"Assessment now published in {classroom.name}: {instance.name}",
                url=f"/student/classroom/{classroom.id}/assessment"
            )
            recipients = classroom.get_all_student().values_list('user', flat=True)
            notification.recipients.add(*recipients)
@receiver(post_save, sender=Submission)
def notify_teacher_on_submission(sender, instance, created, **kwargs):
    if created:
        assessment = instance.assessment
        classroom = assessment.classroom
        teacher_user = classroom.teacher.user

        notification = Notification.objects.create(
            sender=instance.student.user,  
            message=f"{instance.student} submitted '{assessment.name}' in {classroom.name}",
            url=f"/teacher/classroom/{classroom.id}/assessment"
        )
        notification.recipients.add(teacher_user)


@receiver(post_save, sender=ForumMessage)
def notify_classroom_on_forum_message(sender, instance, created, **kwargs):
    if not created:
        return 
    classroom = instance.classroom
    sender_user = instance.sender
    students_users = classroom.get_all_student().values_list('user', flat=True)
    teacher_user_id = classroom.teacher.user.id if hasattr(classroom.teacher, 'user') else None
    recipient_ids = set(students_users)
    if teacher_user_id:
        recipient_ids.add(teacher_user_id)
    recipient_ids.discard(sender_user.id)
    if not recipient_ids:
        return  
    if hasattr(sender_user, 'teacher_profile'):
        basePath = 'teacher'
    elif hasattr(sender_user, 'student_profile'):
        basePath = 'student'
    notification = Notification.objects.create(
        sender=sender_user,
        message=f"New forum message in {classroom.name}: {instance.content[:50]}...",
        url=f"/{basePath}/classroom/{classroom.id}/discussion"
    )
    notification.recipients.add(*recipient_ids)







