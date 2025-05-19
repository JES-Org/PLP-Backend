from django.db import models
from classrooms.models import Classroom
from users.models import Teacher, Student

class Assessment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tag = models.CharField(max_length=100)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assessments')
    is_published = models.BooleanField(default=False)
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    text = models.TextField()
    weight = models.FloatField(default=1.0)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    tags = models.JSONField(default=list, blank=True)  # List of strings
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='submissions')
    answers = models.JSONField()
    score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'assessment')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.assessment.name}"
