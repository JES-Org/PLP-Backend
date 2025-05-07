from django.db import models
from django.core.exceptions import ValidationError
from users.models import Teacher, Student

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.name

class Batch(models.Model):
    section = models.CharField(max_length=10)
    year = models.PositiveIntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, related_name='batches', blank=True)

    class Meta:
        unique_together = ('section', 'year', 'department')

    def __str__(self):
        return f"{self.department.name}-{self.year}-{self.section}"

class Classroom(models.Model):
    name = models.CharField(max_length=255)
    courseNo = models.CharField(max_length=50)
    description = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='created_classrooms')
    batches = models.ManyToManyField(Batch, related_name='classrooms', blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    class_room = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='announcements')
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
class Attachment(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='announcements/')

    def __str__(self):
        return f"Attachment for {self.announcement.title} - {self.file.name}"


class Message(models.Model):
    content = models.TextField()
    sender_teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_messages_as_teacher'
    )
    sender_student = models.ForeignKey(
        Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_messages_as_student'
    )
    receiver_teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_messages_as_teacher'
    )
    receiver_student = models.ForeignKey(
        Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_messages_as_student'
    )
    class_room = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name='messages'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def sender(self):
        return self.sender_teacher or self.sender_student

    @property
    def receiver(self):
        return self.receiver_teacher or self.receiver_student
    
    class Meta:
        ordering = ["-created_at"]


    def clean(self):
        if bool(self.sender_teacher) == bool(self.sender_student):
            raise ValidationError('Specify exactly one sender: teacher or student.')

        if bool(self.receiver_teacher) == bool(self.receiver_student):
            raise ValidationError('Specify exactly one receiver: teacher or student.')

    def __str__(self):
        sender_obj = self.sender
        sender_display = "Unknown Sender"
        if sender_obj:
            sender_display = str(sender_obj)

        receiver_obj = self.receiver
        receiver_display = "Unknown Receiver"
        if receiver_obj:
            receiver_display = str(receiver_obj)

        classroom_name = (
            self.class_room.name if self.class_room else "Unknown Classroom"
        )
       
        content_preview = (
            (self.content[:30] + "...")
            if len(self.content) > 30
            else self.content
        )

        return (
            f"Msg in {classroom_name} from {sender_display} to {receiver_display}: "
            f"'{content_preview}'"
        )
