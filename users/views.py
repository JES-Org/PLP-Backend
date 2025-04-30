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
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)

        # return full profile based on role
        role = user.role
        if role == "student":
            profile_serializer = StudentSerializer(user.student_profile)
        elif role == "teacher":
            profile_serializer = TeacherSerializer(user.teacher_profile)
        else:
            profile_serializer = UserSerializer(user)

        return Response(
            {
                "user": profile_serializer.data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
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
