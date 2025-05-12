from rest_framework import serializers
from .models import Assessment, Question, Answer, Submission
from classrooms.models import Classroom
from users.models import Student

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'created_at', 'updated_at']

class CreateQuestionSerializer(serializers.Serializer):
    text = serializers.CharField()
    weight = serializers.FloatField()
    assessmentId = serializers.IntegerField()
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    answers = serializers.ListField(child=serializers.CharField(), min_length=2)
    correctAnswerIndex = serializers.IntegerField()

    def validate(self, data):
        if data['correctAnswerIndex'] >= len(data['answers']):
            raise serializers.ValidationError("Correct answer index is out of range.")
        return data

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
        read_only_fields = ['created_at', 'updated_at']

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