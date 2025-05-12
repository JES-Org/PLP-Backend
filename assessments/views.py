from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied

from django.utils import timezone

from classrooms.models import Classroom
from .models import Answer, Assessment, Question
from .serializers import AssessmentSerializer, CreateQuestionSerializer, QuestionSerializer

class AssessmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, classroom_id):
        user = request.user

        if user.role == 'student':
            assessments = Assessment.objects.filter(classroom_id=classroom_id, is_published=True)
        else:
            assessments = Assessment.objects.filter(classroom_id=classroom_id)

        serializer = AssessmentSerializer(assessments, many=True)
        return Response({
            "isSuccess": True,
            "message": "Assessments retrieved successfully.",
            "data": serializer.data,
            "errors": []
        }, status=status.HTTP_200_OK)

    def post(self, request, classroom_id):
        data = request.data.copy()
        data['classroom'] = classroom_id
        print("Data received:", data)
        serializer = AssessmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "isSuccess": True,
                "message": "Assessment created successfully.",
                "data": serializer.data,
                "errors": []
            }, status=status.HTTP_201_CREATED)
        return Response({
            "isSuccess": False,
            "message": "Assessment creation failed.",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class AssessmentPublishView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, classroom_id, id):
        print("Publishing assessment with ID:", id, " for classroom ID:", classroom_id)
        try:
            assessment = Assessment.objects.get(id=id, classroom_id=int(classroom_id))
            print("Assessment found:", assessment)
        except Assessment.DoesNotExist:
            return Response({
                "isSuccess": False,
                "message": "Assessment not found",
                "data": None,
                "errors": ["Assessment not found for the given classroom."]
            }, status=status.HTTP_404_NOT_FOUND)

        if assessment.is_published:
            return Response({
                "isSuccess": False,
                "message": "Assessment could not be published",
                "data": None,
                "errors": ["Assessment is already published."]
            }, status=status.HTTP_400_BAD_REQUEST)

        if assessment.deadline < timezone.now():
            return Response({
                "isSuccess": False,
                "message": "Assessment could not be published",
                "data": None,
                "errors": ["Assessment deadline is expired."]
            }, status=status.HTTP_400_BAD_REQUEST)

        assessment.is_published = True
        assessment.save()

        serializer = AssessmentSerializer(assessment)

        return Response({
            "isSuccess": True,
            "message": "Assessment published successfully.",
            "data": serializer.data,
            "errors": []
        }, status=status.HTTP_200_OK)

class AssessmentDetailView(generics.RetrieveAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        classroom_id = self.kwargs.get("classroom_id")
        assessment_id = self.kwargs.get("id")

        try:
            assessment = Assessment.objects.get(id=assessment_id, classroom_id=classroom_id)
        except Assessment.DoesNotExist:
            raise NotFound(detail="Assessment not found")

        # Optional: restrict unpublished access for students
        user = self.request.user
        if user.role == "student" and not assessment.is_published:
            raise PermissionDenied(detail="Assessment is not published")

        return assessment

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "isSuccess": True,
            "message": "Assessment retrieved successfully.",
            "data": serializer.data,
            "errors": []
        })

class AddQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, classroom_id):
        serializer = CreateQuestionSerializer(data=request.data)
        print("Request data for adding question:", request.data)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response({
                "isSuccess": False,
                "message": "Question could not be created",
                "data": None,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        try:
            assessment = Assessment.objects.get(id=validated['assessmentId'], classroom_id=classroom_id)
        except Assessment.DoesNotExist:
            return Response({
                "isSuccess": False,
                "message": "Assessment not found",
                "data": None,
                "errors": ["No assessment with the given ID in this classroom."]
            }, status=status.HTTP_404_NOT_FOUND)

        question = Question.objects.create(
            text=validated['text'],
            weight=validated['weight'],
            assessment=assessment,
            tags=validated.get('tags', [])
        )

        for idx, answer_text in enumerate(validated['answers']):
            Answer.objects.create(
                question=question,
                text=answer_text,
                is_correct=(idx == validated['correctAnswerIndex'])
            )

        response_data = QuestionSerializer(question).data
        return Response({
            "isSuccess": True,
            "message": "Question created successfully.",
            "data": response_data,
            "errors": []
        }, status=status.HTTP_201_CREATED)