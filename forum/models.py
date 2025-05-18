from django.db import models
from classrooms.models import Classroom
from django.contrib.auth import get_user_model

User = get_user_model()

class ForumMessage(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='forum_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender} - {self.content[:30]}"