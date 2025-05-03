from rest_framework import generics, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    TeacherSerializer,
    StudentSerializer,
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
)

ROLE_MAP = {"student": 0, "teacher": 1, "admin": 2}


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
        response = super().post(request, *args, **kwargs)
        try:
            user = User.objects.get(email=request.data["email"])
            if user.role == "student":
                response.data["user"] = StudentSerializer(user.student_profile).data
            elif user.role == "teacher":
                response.data["user"] = TeacherSerializer(user.teacher_profile).data
            else:
                response.data["user"] = UserSerializer(user).data
        except User.DoesNotExist:
            response.data["user"] = None
        return response
