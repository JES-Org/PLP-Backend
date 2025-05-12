from rest_framework import serializers
from .models import Assessment, Question, Answer, Submission
from classrooms.models import Classroom
from users.models import Student

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'created_at', 'updated_at']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id',
            'text',
            'weight',
            'tags',
            'assessment',
            'answers',
            'created_at',
            'updated_at',
        ]

class AssessmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    classroom = serializers.StringRelatedField()  # or use ClassroomSerializer if you want more detail

    class Meta:
        model = Assessment
        fields = [
            'id',
            'name',
            'description',
            'tag',
            'classroom',
            'is_published',
            'deadline',
            'questions',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['is_published', 'created_at', 'updated_at']

class SubmissionSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    assessment = serializers.StringRelatedField()

    class Meta:
        model = Submission
        fields = [
            'id',
            'student',
            'assessment',
            'answers',
            'score',
            'created_at',
            'updated_at',
        ]