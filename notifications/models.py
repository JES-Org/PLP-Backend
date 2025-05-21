from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    recipients = models.ManyToManyField(User, related_name="notifications")
    sender = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='sent_notifications')
    message = models.TextField()
    url = models.URLField(blank=True, null=True)
    is_read_by = models.ManyToManyField(User, related_name="read_notifications", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to users - {self.message[:20]}"
