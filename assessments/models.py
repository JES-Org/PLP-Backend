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
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('short_answer', 'Short Answer'),
    ]

    text = models.TextField()
    weight = models.FloatField(default=1.0)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        default='multiple_choice'
    )
    model_answer = models.TextField(blank=True, null=True)
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
    graded_details = models.JSONField(null=True, blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'assessment')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.assessment.name}"
    
    def calculate_total_score(self):
        new_total_score = 0
        assessment_questions = self.assessment.questions.all().prefetch_related('answers')

        for question in assessment_questions:
            if question.question_type == 'multiple_choice':
                student_answer_id = self.answers.get(str(question.id))
                correct_answer_option = question.answers.filter(is_correct=True).first()
                if correct_answer_option and student_answer_id == str(correct_answer_option.id):
                    new_total_score += question.weight
        
        if self.graded_details:
            for question_id_str, assigned_score in self.graded_details.items():
                try:
                    question = Question.objects.get(id=question_id_str)
                    if question.question_type == 'short_answer':
                         if isinstance(assigned_score, (int, float)):
                            new_total_score += assigned_score
                except Question.DoesNotExist:
                    pass
                except ValueError:
                    pass


        self.score = new_total_score
