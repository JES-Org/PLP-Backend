# models.py
from django.db import models
from classrooms.models import Classroom

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('announcement', 'Announcement'),
        ('assignment', 'Assignment'),
        ('forum', 'Forum Post'),
    )
    
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_object_id = models.PositiveIntegerField()  # ID of the related object (announcement, etc.)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
