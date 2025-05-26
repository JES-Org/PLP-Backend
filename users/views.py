from datetime import timedelta
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError

import logging
import random
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import User, Student, Teacher, Otp
from .utils import send_otp_email
from .serializers import (
    TeacherSerializer,
    StudentSerializer,
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
)
from classrooms.models import Batch
from django.http import Http404

User = get_user_model()

ROLE_MAP = {"student": 0, "teacher": 1, "admin": 2}
ROLE_REVERSE_MAP = {0: "student", 1: "teacher", 2: "admin"}
logger = logging.getLogger(__name__)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    return {
        "refresh": str(refresh),
        "access": str(access),
    }


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            tokens = get_tokens_for_user(user)

            data = {
                "id": str(user.id),
                "email": user.email,
                "role": ROLE_MAP.get(user.role, -1),
                "token": tokens["access"],
                "refresh": tokens["refresh"],
                 "isVerified": False,  # Adjust if using email verification logic
            }

            return Response(
                {
                    "isSuccess": True,
                    "message": "User registered successfully",
                    "data": data,
                    "errors": [],
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {
                    "isSuccess": False,
                    "message": "User registration failed",
                    "data": None,
                    "errors": [str(e)],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            response = super().post(request, *args, **kwargs)
            email = request.data.get("email")
            user = User.objects.get(email=email,)

            teacher_data = None
            student_data = None

            if user.role == "teacher":
                try:
                    teacher = user.teacher_profile
                    teacher_data = TeacherSerializer(teacher).data
                except Teacher.DoesNotExist:
                    teacher_data = None
            elif user.role == "student":
                try:
                    student = user.student_profile
                    student_data = StudentSerializer(student).data
                except Student.DoesNotExist:
                    student_data = None

            return Response(
                {
                    "isSuccess": True,
                    "message": "Login successful",
                    "data": {
                        "id": str(user.id),
                        "email": user.email,
                        "role": ROLE_MAP.get(user.role, -1),
                        "token": response.data.get("access"),
                        "refresh": response.data.get("refresh"),
                        "teacher": teacher_data,
                        "student": student_data,
                    },
                    "errors": [],
                },
                status=status.HTTP_200_OK,
            )
        
        except TokenError as e:
            return Response({
                "isSuccess": False,
                "message": "Token generation error.",
                "data": None,
                "errors": [str(e)],
            }, status=status.HTTP_400_BAD_REQUEST)

        except AuthenticationFailed as e:
            error_detail = e.detail
            error_message = str(error_detail.get('detail')) if isinstance(error_detail, dict) else str(error_detail)
            error_code = e.get_codes()
            
            return Response({
                "isSuccess": False,
                "message": error_message,
                "data": None,
                "errors": [error_code] if isinstance(error_code, str) else error_code,
            }, status=e.status_code)
            
        except Exception as e:
            return Response({
                "isSuccess": False,
                "message": "Invalid credentials",
                "data": None,
                "errors": [str(e)],
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    email = request.data.get("email")

    if not email:
        return Response(
            {
                "isSuccess": False,
                "message": "Email is required.",
                "data": None,
                "errors": ["Email field is missing or empty."],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)
        user_name = "User"
    except User.DoesNotExist:
        return Response(
            {
                "isSuccess": False,
                "message": "User not found.",
                "data": None,
                "errors": [f"No user associated with the email: {email}"],
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        print(f"Error fetching user {email}: {str(e)}") # Server-side log
        return Response(
            {
                "isSuccess": False,
                "message": "An error occurred while processing your request.",
                "data": None,
                "errors": ["Server error retrieving user information."],
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        otp_code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)
        
        Otp.objects.filter(user=user).delete()
        Otp.objects.create(user=user, code=otp_code, expires_at=expires_at)

        email_sent_successfully = send_otp_email(user.email, otp_code, user_name)

        if not email_sent_successfully:
            return Response(
                {
                    "isSuccess": False,
                    "message": "Failed to send OTP email. Please try again later or contact support.",
                    "data": None,
                    "errors": ["Email service provider encountered an issue."],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "isSuccess": True,
                "message": "An OTP has been sent to your email address.",
                "data": None,
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        print(f"Unexpected error during OTP processing for {email}: {str(e)}") # Server-side log
        return Response(
            {
                "isSuccess": False,
                "message": "An unexpected error occurred while sending the OTP.",
                "data": None,
                "errors": ["An internal server error occurred."],
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    code = request.data.get("otp")
    email = request.data.get("email")

    if not code or not email:
        return Response(
            {
                "isSuccess": False,
                "message": "Email and OTP are required.",
                "data": None,
                "errors": ["Email and OTP fields must not be empty."],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {
                "isSuccess": False,
                "message": "Invalid email or OTP.",
                "data": None,
                "errors": ["The provided email or OTP is incorrect or has expired."],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        print(f"Error fetching user {email} during OTP verification: {str(e)}")
        return Response(
            {
                "isSuccess": False,
                "message": "An error occurred while verifying OTP.",
                "data": None,
                "errors": ["Server error processing user information."],
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        otp_obj = Otp.objects.filter(
            user=user,
            code=code,
            expires_at__gt=timezone.now()
        ).order_by("-created_at").first()

        if not otp_obj:
            return Response(
                {
                    "isSuccess": False,
                    "message": "Invalid or expired OTP.",
                    "data": None,
                    "errors": ["The provided OTP is incorrect, has already been used, or has expired."],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_obj.save()

        profile_updated = False
        if user.role == "student":
            student_profile = getattr(user, 'student_profile', None)
            if student_profile:
                student_profile.is_verified = True
                student_profile.save()
                profile_updated = True
            else:
                print(f"Warning: Student user {user.email} has no student_profile to verify.")
        elif user.role == "teacher":
            teacher_profile = getattr(user, 'teacher_profile', None)
            if teacher_profile:
                teacher_profile.is_verified = True
                teacher_profile.save()
                profile_updated = True
            else:
                print(f"Warning: Teacher user {user.email} has no teacher_profile to verify.")

        success_message = "OTP verified successfully."
        if profile_updated:
            success_message += " Profile updated."
        elif user.role in ["student", "teacher"]:
            success_message += " No profile found to update verification status."


        return Response(
            {
                "isSuccess": True,
                "message": success_message,
                "data": {"status": "verified"},
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        print(f"Unexpected error during OTP verification for {email}: {str(e)}")
        return Response(
            {
                "isSuccess": False,
                "message": "OTP verification failed due to an unexpected error.",
                "data": None,
                "errors": ["An internal server error occurred during verification."],
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

class GetTeacherByUserIdView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, role="teacher")
            teacher_profile = user.teacher_profile
            serializer = TeacherSerializer(teacher_profile)

            return Response({
                "isSuccess": True,
                "message": "Teacher retrieved successfully",
                "data": serializer.data,
                "errors": []
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "isSuccess": False,
                "message": "Teacher not found",
                "data": None,
                "errors": [str(e)]
            }, status=status.HTTP_404_NOT_FOUND)


class GetStudentByUserIdView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, role="student")
            student_profile = user.student_profile
            serializer = StudentSerializer(student_profile)

            return Response({
                "isSuccess": True,
                "message": "Student retrieved successfully",
                "data": serializer.data,
                "errors": []
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "isSuccess": False,
                "message": "Student not found",
                "data": None,
                "errors": [str(e)]
            }, status=status.HTTP_404_NOT_FOUND)

class GetStudentByIdView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            serializer = StudentSerializer(student)
            return Response({
                "isSuccess": True,
                "message": "Student retrieved successfully",
                "data": serializer.data,
                "errors": []
            }, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({
                "isSuccess": False,
                "message": "Student not found",
                "data": None,
                "errors": ["Invalid student ID."]
            }, status=status.HTTP_404_NOT_FOUND)

class GetTeacherByIdView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            serializer = TeacherSerializer(teacher)
            return Response({
                "isSuccess": True,
                "message": "Teacher retrieved successfully",
                "data": serializer.data,
                "errors": []
            }, status=status.HTTP_200_OK)
        except Teacher.DoesNotExist:
            return Response({
                "isSuccess": False,
                "message": "Teacher not found",
                "data": None,
                "errors": ["Invalid teacher ID."]
            }, status=status.HTTP_404_NOT_FOUND)

        
class UpdateStudentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            return user.student_profile
        except Exception as e:
            logger.error(f"Error retrieving student profile: {e}")
            raise Http404("Student profile not found")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Convert frontend data to expected format
        request_data = request.data.copy()
        
        # If department/section/year are provided, find/create matching batch
        if all(k in request_data for k in ['department', 'section', 'year']):
            try:
                batch, created = Batch.objects.get_or_create(
                    department_id=request_data['department'],
                    section=request_data['section'],
                    year=request_data['year']
                )
                request_data['batch'] = batch.id
            except Exception as e:
                logger.error(f"Error processing batch data: {e}")
                return Response({
                    "isSuccess": False,
                    "message": "Invalid batch data",
                    "errors": [str(e)]
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request_data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "isSuccess": True,
                "message": "Profile updated successfully",
                "data": serializer.data
            })
        
        return Response({
            "isSuccess": False,
            "message": "Update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class UpdateTeacherProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.teacher_profile
    
    def update(self, request, *args, **kwargs):
        print("🟢 Incoming data:", request.data)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if not serializer.is_valid():
            print("🔴 Serializer errors:", serializer.errors)
            return Response({
                    "isSuccess": False,
                    "message": "Teacher not found",
                    "data": None,
                    "errors": [serializer.errors]
                }, status=status.HTTP_404_NOT_FOUND)

        self.perform_update(serializer)
        return Response({
                "isSuccess": True,
                "message": "Teacher retrieved successfully",
                "data": serializer.data,
                "errors": []
            }, status=status.HTTP_200_OK)
    

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User with this email not found'}, status=status.HTTP_404_NOT_FOUND)