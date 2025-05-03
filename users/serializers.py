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
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    dob = serializers.DateField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)
    department = serializers.CharField(write_only=True, required=False)
    student_id = serializers.CharField(write_only=True, required=False)
    year = serializers.IntegerField(write_only=True, required=False)
    section = serializers.CharField(write_only=True, required=False)
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "role",
            "first_name",
            "last_name",
            "dob",
            "phone",
            "department",
            "student_id",
            "year",
            "section",
            "image",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        role = validated_data["role"]

        # pop all profile fields
        student_id = validated_data.pop("student_id", None)
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        dob = validated_data.pop("dob")
        phone = validated_data.pop("phone")
        department = validated_data.pop("department")
        year = validated_data.pop("year", None)
        section = validated_data.pop("section", None)
        image = validated_data.pop("image", None)

        # create user
        user = User.objects.create_user(**validated_data)

        if role == "teacher":
            Teacher.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                dob=dob,
                phone=phone,
                department=department,
                image=image,
            )
        elif role == "student":
            Student.objects.create(
                user=user,
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                dob=dob,
                phone=phone,
                department=department,
                year=year,
                section=section,
                image=image,
            )

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
        token["role"] = user.role
        return token


class StudentSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    role = serializers.SerializerMethodField()
    imageUrl = serializers.ImageField(source="image", read_only=True)

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
