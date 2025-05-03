from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import authenticate

from .models import User, Teacher, Student

ROLE_MAP = {"student": 0, "teacher": 1, "admin": 2}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "role",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        if user.role == "student":
            Student.objects.create(user=user)
        elif user.role == "teacher":
            Teacher.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = ROLE_MAP.get(user.role, -1)
        return token


class StudentSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    role = serializers.SerializerMethodField()
    imageUrl = serializers.ImageField(source="image", read_only=True)
    id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "student_id",
            "first_name",
            "last_name",
            "email",
            "dob",
            "phone",
            "join_date",
            "year",
            "section",
            "department",
            "imageUrl",
            "role",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "role", "user"]

    def get_role(self, obj):
        return ROLE_MAP.get(obj.user.role, -1)


class TeacherSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    role = serializers.SerializerMethodField()
    imageUrl = serializers.ImageField(source="image", read_only=True)
    id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "dob",
            "phone",
            "join_date",
            "department",
            "imageUrl",
            "role",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "role", "user"]

    def get_role(self, obj):
        return ROLE_MAP.get(obj.user.role, -1)
