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
    question_type = serializers.ChoiceField(choices=Question.QUESTION_TYPES, default='multiple_choice')
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    model_answer = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    answers = serializers.ListField(child=serializers.CharField(max_length=255), required=False, default=[])
    correctAnswerIndex = serializers.IntegerField(required=False, allow_null=True, min_value=-1)

    def validate(self, data):
        if data.get('question_type') == 'multiple_choice':
            if not data.get('answers') or len(data.get('answers')) < 2:
                raise serializers.ValidationError({"answers": "Multiple choice questions require at least two answer options."})
            if data.get('correctAnswerIndex') is None or data.get('correctAnswerIndex') < 0 or data.get('correctAnswerIndex') >= len(data.get('answers')):
                raise serializers.ValidationError({"correctAnswerIndex": "A valid correct answer must be selected for multiple choice questions."})
        elif data.get('question_type') == 'short_answer':
            # For short answers, 'answers' and 'correctAnswerIndex' are ignored or should be empty
            data['answers'] = []
            data['correctAnswerIndex'] = -1 # Or None
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
            'question_type',
            'model_answer',
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

class CreateSubmissionSerializer(serializers.Serializer):
    studentId = serializers.IntegerField()
    assessmentId = serializers.IntegerField()
    answers = serializers.DictField(
        child=serializers.CharField(allow_blank=True)
    )

    def validate_answers(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Answers must be a dictionary/map.")
        for q_id, ans_text in value.items():
            if not isinstance(ans_text, str):
                raise serializers.ValidationError(f"Answer for question ID {q_id} must be a string.")
        return value

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

class GradeShortAnswerSerializer(serializers.Serializer):
    question_scores = serializers.DictField(
        child=serializers.FloatField(min_value=0)
    )

    def validate_question_scores(self, value):
        for question_id_str, score in value.items():
            try:
                question = Question.objects.get(id=question_id_str)
                if question.question_type != 'short_answer':
                    raise serializers.ValidationError(
                        f"Question ID {question_id_str} is not a short answer question."
                    )
                if score > question.weight:
                    raise serializers.ValidationError(
                        f"Score {score} for question ID {question_id_str} exceeds its maximum weight of {question.weight}."
                    )
            except Question.DoesNotExist:
                raise serializers.ValidationError(f"Question with ID {question_id_str} not found.")
            except ValueError:
                raise serializers.ValidationError(f"Invalid format for question ID {question_id_str}.")
        return value

class AnalyticsSerializer(serializers.Serializer):
    meanScore = serializers.FloatField()
    medianScore = serializers.FloatField()
    modeScore = serializers.FloatField(allow_null=True)
    standardDeviation = serializers.FloatField()
    variance = serializers.FloatField()
    highestScore = serializers.FloatField()
    lowestScore = serializers.FloatField()
    range = serializers.FloatField()
    totalSubmissions = serializers.IntegerField()