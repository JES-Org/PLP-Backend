from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

import random

from .models import User, Student, Teacher, Otp
from .serializers import (
    TeacherSerializer,
    StudentSerializer,
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
)

ROLE_MAP = {"student": 0, "teacher": 1, "admin": 2}
ROLE_REVERSE_MAP = {0: "student", 1: "teacher", 2: "admin"}


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
            response = super().post(request, *args, **kwargs)
            email = request.data.get("email")
            user = User.objects.get(email=email)

            return Response(
                {
                    "isSuccess": True,
                    "message": "Login successful",
                    "data": {
                        "id": str(user.id),
                        "email": user.email,
                        "role": ROLE_MAP.get(user.role, -1),
                        "token": response.data.get("access"),
                    },
                    "errors": [],
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "isSuccess": False,
                    "message": "Login failed",
                    "data": None,
                    "errors": [str(e)],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    try:
        email = request.data.get("email")
        user_id = request.data.get("userId")
        role_num = request.data.get("role")

        role = ROLE_REVERSE_MAP.get(role_num)

        user = User.objects.get(id=user_id, email=email, role=role)

        otp_code = str(random.randint(100000, 999999))
        Otp.objects.create(user=user, code=otp_code)

        # TODO: send this via actual email; for now just print/log
        print(f"[OTP] Code for {user.email}: {otp_code}")

        return Response(
            {
                "isSuccess": True,
                "message": "OTP sent successfully.",
                "data": None,
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                "isSuccess": False,
                "message": "Failed to send OTP",
                "data": None,
                "errors": [str(e)],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    try:
        code = request.data.get("otp")
        user_id = request.data.get("userId")
        role_num = request.data.get("role")

        role = ROLE_REVERSE_MAP.get(role_num)
        user = User.objects.get(id=user_id, role=role)

        otp_obj = (
            Otp.objects.filter(user=user, code=code).order_by("-created_at").first()
        )

        if not otp_obj or otp_obj.is_expired():
            return Response(
                {
                    "isSuccess": False,
                    "message": "Invalid or expired OTP",
                    "data": None,
                    "errors": ["Invalid or expired OTP"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark user as verified (update related profile)
        if role == "student" and hasattr(user, "student_profile"):
            user.student_profile.is_verified = True
            user.student_profile.save()
        elif role == "teacher" and hasattr(user, "teacher_profile"):
            user.teacher_profile.is_verified = True
            user.teacher_profile.save()

        otp_obj.delete()

        return Response(
            {
                "isSuccess": True,
                "message": "OTP verified successfully",
                "data": "verified",
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                "isSuccess": False,
                "message": "OTP verification failed",
                "data": None,
                "errors": [str(e)],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

class GetTeacherByUserIdView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, role="teacher")
            teacher_profile = user.teacher_profile
            serializer = TeacherSerializer(teacher_profile)

            data = transform_teacher_response(serializer.data)

            return Response({
                "isSuccess": True,
                "message": "Teacher retrieved successfully",
                "data": data,
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

            data = transform_student_response(serializer.data)

            return Response({
                "isSuccess": True,
                "message": "Student retrieved successfully",
                "data": data,
                "errors": []
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "isSuccess": False,
                "message": "Student not found",
                "data": None,
                "errors": [str(e)]
            }, status=status.HTTP_404_NOT_FOUND)

class UpdateStudentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.student_profile
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        data = transform_student_response(serializer.data)

        return Response({
            "isSuccess": True,
            "message": "Profile updated successfully",
            "data": data,
            "errors": []
        }, status=status.HTTP_200_OK)

class UpdateTeacherProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.teacher_profile
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        data = transform_teacher_response(serializer.data)

        return Response({
            "isSuccess": True,
            "message": "Profile updated successfully",
            "data": data,
            "errors": []
        }, status=status.HTTP_200_OK)

def transform_student_response(data):
    return {
        "id": data.get("id"),
        "studentId": data.get("student_id"),
        "firstName": data.get("first_name"),
        "lastName": data.get("last_name"),
        "dateOfBirth": data.get("dob"),
        "phoneNumber": data.get("phone"),
        "joinDate": data.get("join_date"),
        "year": data.get("year"),
        "section": data.get("section"),
        "department": data.get("department"),
        "email": data.get("email"),
        "role": data.get("role"),
        "isVerified": data.get("is_verified"),
        "imageUrl": data.get("imageUrl"),
        "createdAt": data.get("created_at"),
        "updatedAt": data.get("updated_at"),
    }

def transform_teacher_response(data):
    print(data)
    return {
        "id": data.get("id"),
        "firstName": data.get("first_name"),
        "lastName": data.get("last_name"),
        "dateOfBirth": data.get("dob"),
        "phoneNumber": data.get("phone"),
        "joinDate": data.get("join_date"),
        "department": data.get("department"),
        "email": data.get("email"),
        "role": data.get("role"),
        "isVerified": data.get("is_verified"),
        "imageUrl": data.get("imageUrl"),
        "createdAt": data.get("created_at"),
        "updatedAt": data.get("updated_at"),
    }
