from django.db import models
import secrets
from django.contrib.auth import get_user_model



User=get_user_model()
# class LearningPath(models.Model):
#     student = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     deadline= models.DateTimeField(null=True, blank=True)
#     isCompleted = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.title} (ID: {self.id})"
    
class LearningPath(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (ID: {self.id})"

    @property
    def completion_percentage(self):
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(is_completed=True).count()
        return (completed_tasks / total_tasks) * 100



# models.py
class Task(models.Model):
    CATEGORY_CHOICES = (
        ('PREREQUISITE', 'Prerequisite'),
        ('WEEK', 'Weekly Task'),
        ('RESOURCE', 'Resource'),
    )
    
    learning_path = models.ForeignKey(LearningPath, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    week_number = models.IntegerField(null=True, blank=True)
    day_range = models.CharField(max_length=50, null=True, blank=True)
    week_title = models.CharField(max_length=255, blank=True)
    is_completed = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']




class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_ai_response = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user} - {'AI' if self.is_ai_response else 'User'}"