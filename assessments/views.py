from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied

from django.utils import timezone

from assessments.services.analytics_service import AnalyticsService
from classrooms.models import Classroom
from users.models import Student, User
from .models import Answer, Assessment, Question, Submission
from .serializers import AnalyticsSerializer, AssessmentSerializer, CreateQuestionSerializer, CreateSubmissionSerializer, QuestionSerializer

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
        print("error",serializer.errors)
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

class AssessmentUnpublishView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, classroom_id, id):
        print("Unpublishing assessment with ID:", id, " for classroom ID:", classroom_id)
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
        if not assessment.is_published:
            return Response({
                "isSuccess": False,
                "message": "Assessment could not be unpublished",
                "data": None,
                "errors": ["Assessment is already unpublished."]
            }, status=status.HTTP_400_BAD_REQUEST)
        # Unpublish the assessment
        assessment.is_published = False
        assessment.save()
        serializer = AssessmentSerializer(assessment)
        return Response({
            "isSuccess": True,
            "message": "Assessment unpublished successfully.",
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

class DeleteQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, classroom_id, question_id):
        if request.user.role == 'student':
            return Response({
                "isSuccess": False,
                "message": "Permission denied.",
                "data": None,
                "errors": ["Students are not allowed to delete questions."]
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            print("Deleting question with ID:", question_id, " for classroom ID:", classroom_id)
            question = Question.objects.get(id=question_id, assessment__classroom_id=str(classroom_id))
            print("Question found:", question)
        except Question.DoesNotExist:
            return Response({
                "isSuccess": False,
                "message": "Question not found.",
                "data": None,
                "errors": ["Question not found in this classroom or does not exist."]
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({
                "isSuccess": False,
                "message": "Invalid ID format.",
                "data": None,
                "errors": ["The provided ID for the question or classroom is not valid."]
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            question_id_to_return = question.id
            question.delete()
            return Response({
                "isSuccess": True,
                "message": "Question deleted successfully.",
                "data": {"id": str(question_id_to_return)},
                "errors": []
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "isSuccess": False,
                "message": "Failed to delete question due to a server error.",
                "data": None,
                "errors": [str(e)]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddSubmissionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, classroom_id):
        serializer = CreateSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response({
                "isSuccess": False,
                "message": "Submission could not be created",
                "data": None,
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            assessment = Assessment.objects.get(
                id=data["assessmentId"], classroom_id=classroom_id
            )
            print("assessment: ", assessment)
        except Assessment.DoesNotExist:
            return Response({
                "isSuccess": False,
                "message": "Assessment not found",
                "data": None,
                "errors": ["Invalid assessment for this classroom."]
            }, status=status.HTTP_404_NOT_FOUND)

        if not assessment.is_published:
            return Response({
                "isSuccess": False,
                "message": "Assessment could not be created",
                "data": None,
                "errors": ["Assessment is not published."]
            }, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() > assessment.deadline:
            print("Assessment deadline passed")
            return Response({
                "isSuccess": False,
                "message": "Assessment could not be created",
                "data": None,
                "errors": ["Assessment deadline is passed."]
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(id=data["studentId"])
            print("student: ", student)
        except Student.DoesNotExist:
            print("studnet not found", data["studentId"])
            return Response({
                "isSuccess": False,
                "message": "Submission could not be created",
                "data": None,
                "errors": ["Student not found."]
            }, status=status.HTTP_404_NOT_FOUND)
        
        existing_submission = Submission.objects.filter(
            student=student,
            assessment=assessment
        ).first()

        if existing_submission:
            return Response({
                "isSuccess": False,
                "message": "Submission failed.",
                "data": None,
                "errors": ["You have already submitted this assessment."]
            }, status=status.HTTP_400_BAD_REQUEST)

        questions = assessment.questions.all().order_by('id')
        if len(data["answers"]) != len(questions):
            return Response({
                "isSuccess": False,
                "message": "Submission could not be created",
                "data": None,
                "errors": ["Number of answers does not match number of questions."]
            }, status=status.HTTP_400_BAD_REQUEST)

        question_answer_map = {
            str(question.id): answer_id
            for question, answer_id in zip(questions, data["answers"])
        }

        total_score = 0
        for question in questions:
            selected_answer_id = str(question_answer_map.get(str(question.id)))
            correct_answer = question.answers.filter(is_correct=True).first()
            if correct_answer and str(correct_answer.id) == selected_answer_id:
                total_score += question.weight

        submission = Submission.objects.create(
            student=student,
            assessment=assessment,
            answers=question_answer_map,
            score=total_score
        )

        return Response({
            "isSuccess": True,
            "message": "Submission created successfully.",
            "data": {
                "id": submission.id,
                "student": submission.student.id,
                "assessment": submission.assessment.id,
                "answers": submission.answers,
                "score": submission.score,
                "createdAt": submission.created_at,
                "updatedAt": submission.updated_at,
            },
            "errors": []
        }, status=status.HTTP_201_CREATED)

class GetSubmissionByStudentAndAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, classroom_id, student_id, assessment_id):
        try:
            submission = Submission.objects.get(
                student_id=student_id,
                assessment_id=assessment_id,
                assessment__classroom_id=classroom_id
            )
        except Submission.DoesNotExist:
            return Response({
                "isSuccess": False,
                "message": "Submission not found",
                "data": None,
                "errors": ["No submission found for the given student and assessment."]
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "isSuccess": True,
            "message": "Submission retrieved successfully.",
            "data": {
                "id": submission.id,
                "student": submission.student.id,
                "assessment": submission.assessment.id,
                "answers": submission.answers,
                "score": submission.score,
                "createdAt": submission.created_at,
                "updatedAt": submission.updated_at,
            },
            "errors": []
        }, status=status.HTTP_200_OK)

class AssessmentAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, classroom_id, assessment_id):
        try:
            assessment = Assessment.objects.get(id=assessment_id, classroom_id=classroom_id)
        except Assessment.DoesNotExist:
            raise NotFound("Assessment not found")
        data = AnalyticsService.perform_class_analysis(assessment.id)
        if not data:
            return Response({
                "isSuccess": False,
                "message": "No data available",
                "data": None,
                "errors": ["No submissions found for this assessment."]
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "isSuccess": True,
            "message": "Analytics retrieved successfully",
            "data": data,
            "errors": []
        }, status=status.HTTP_200_OK)
class AgregateAssessmentAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, classroom_id):
        assessments = Assessment.objects.filter(
            classroom_id=classroom_id,
            submissions__isnull=False
        ).distinct()
        print("Assessments with submissions:", assessments)

        if not assessments.exists():
            return Response({
                "isSuccess": False,
                "message": "No assessments with submissions found",
                "data": None,
                "errors": ["No analytics available for this classroom"]
            }, status=status.HTTP_404_NOT_FOUND)

        analytics_data = {}

        for assessment in assessments:
            data = AnalyticsService.perform_class_analysis(assessment.id)
            if data:
                analytics_data[str(assessment.id)] = {
                    "data": data
                }
            else:
                analytics_data[str(assessment.id)] = {
                    "error": "No analytics data available"
                }
        print("Analytics data:j", analytics_data)
        return Response({
            "isSuccess": True,
            "message": "Analytics retrieved successfully",
            "data": analytics_data,
            "errors": []
        }, status=status.HTTP_200_OK)


class CrossAssessmentAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, classroom_id):
        data = AnalyticsService.perform_cross_assessment(classroom_id)
        return Response({
            "isSuccess": True,
            "message": "Cross-assessment analytics retrieved successfully",
            "data": data,
            "errors": []
        })

class AssessmentAnalyticsByTagView(APIView):
    def post(self, request, classroom_id):
        tags = request.data

        if not tags or not isinstance(tags, list):
            return Response({
                "isSuccess": False,
                "message": "Tags are required",
                "data": None,
                "errors": ["Tags must be a non-empty list."]
            }, status=status.HTTP_400_BAD_REQUEST)

        assessments = Assessment.objects.filter(classroom_id=classroom_id)

        analytics_result = []
        for assessment in assessments:
            if not Question.objects.filter(assessment=assessment, tags__overlap=tags).exists():
                continue

            submissions = Submission.objects.filter(assessment=assessment)

            if submissions.exists():
                scores = [s.score for s in submissions]
                scores.sort()
                total = len(scores)
                mean_score = sum(scores) / total
                median_score = scores[total // 2] if total % 2 != 0 else (scores[total//2 - 1] + scores[total//2]) / 2
                mode_score = max(set(scores), key=scores.count) if scores else None

                data = {
                    "meanScore": mean_score,
                    "medianScore": median_score,
                    "modeScore": mode_score,
                    "standardDeviation": float(Submission.objects.filter(assessment=assessment).aggregate(std=Avg("score"))["std"] or 0),
                    "variance": float(sum((x - mean_score) ** 2 for x in scores) / total),
                    "highestScore": max(scores),
                    "lowestScore": min(scores),
                    "range": max(scores) - min(scores),
                    "totalSubmissions": total,
                }

                analytics_result.append(data)

        serializer = AnalyticsSerializer(data=analytics_result, many=True)
        serializer.is_valid(raise_exception=True)
        return Response({
            "isSuccess": True,
            "message": "Analytics retrieved successfully.",
            "data": serializer.data,
            "errors": []
        })

class GradeStudentsView(APIView):
    def post(self, request, classroom_id):
        student_ids = request.data.get("studentIds", [])
        assessment_id = request.query_params.get("assessmentId")

        if not student_ids:
            return Response({
                "isSuccess": False,
                "message": "Student ids are required",
                "data": None,
                "errors": ["studentIds must be a non-empty list."]
            }, status=status.HTTP_400_BAD_REQUEST)

        if not assessment_id:
            return Response({
                "isSuccess": False,
                "message": "Assessment ID is required",
                "data": None,
                "errors": ["Missing query param: assessmentId"]
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            assessment = Assessment.objects.get(id=assessment_id, classroom_id=classroom_id)
        except Assessment.DoesNotExist:
            return Response({
                "isSuccess": False,
                "message": "Assessment not found",
                "data": None,
                "errors": ["Invalid assessment for this classroom."]
            }, status=status.HTTP_404_NOT_FOUND)

        
        updated = 0
        for student_id in student_ids:
            try:
                submission = Submission.objects.get(student_id=student_id, assessment=assessment)
            except Submission.DoesNotExist:
                continue

            correct_answers = 0
            total_questions = assessment.questions.count()
            answer_map = submission.answers

            for question in assessment.questions.all():
                correct = question.answers.filter(is_correct=True).first()
                if correct and str(question.id) in answer_map and str(correct.id) == str(answer_map[str(question.id)]):
                    correct_answers += 1

            submission.score = round((correct_answers / total_questions) * 100, 2) if total_questions else 0
            submission.save()
            updated += 1

        return Response({
            "isSuccess": True,
            "message": f"{updated} student(s) graded successfully.",
            "data": True,
            "errors": []
        }, status=status.HTTP_200_OK)
