from django.db import models
from django.core.exceptions import ValidationError
from users.models import Teacher, Student
from django.contrib.auth import get_user_model


User = get_user_model()


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
    def get_all_student(self):
        if hasattr(self, '_cached_students'):
            return self._cached_students
            
        self._cached_students = Student.objects.filter(
            batch__in=self.batches.all()
        ).distinct()
        return self._cached_students

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    class_room = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
class Attachment(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='announcements/')
    created_at = models.DateTimeField(auto_now_add=True ,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
  
    def __str__(self):
        return f"Attachment for {self.announcement.title} - {self.file.name}"


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        null=True,
        blank=True

    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='messages',
           null=True,
        blank=True
    )
    content = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['classroom', 'timestamp']),
        ]

    def __str__(self):
        return f"Message from {self.sender} in {self.classroom}"

class MessageReadStatus(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_statuses'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_read_statuses'
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('message', 'user')  
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user} - {'Read' if self.is_read else 'Unread'}"