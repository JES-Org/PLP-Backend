from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import authenticate

from .models import User, Teacher, Student
from django.conf import settings
from classrooms.models import Batch
from classrooms.serializers import BatchSerializer
ROLE_MAP = {"student": 0, "teacher": 1, "admin": 2}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role","is_active", "is_staff"]


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
    email = serializers.EmailField(source='user.email', required=False)
    role = serializers.SerializerMethodField()
    imageUrl = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False)
    batch = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.all(),
        required=False,
        allow_null=True
    )
    batch_details = BatchSerializer(source='batch', read_only=True)
    department = serializers.SerializerMethodField(read_only=True)
    section = serializers.SerializerMethodField(read_only=True)
    year = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id", "student_id", "first_name", "last_name", "email",
            "dob", "phone", "join_date", "batch", "batch_details",
            "department", "section", "year",  # Read-only for compatibility
            "imageUrl", "image", "role", "is_verified",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "role", "batch_details", "department", "section", "year"]
    def get_department(self, obj):
            return obj.batch.department.id if obj.batch else None
        
    def get_section(self, obj):
            return obj.batch.section if obj.batch else None
        
    def get_year(self, obj):
            return obj.batch.year if obj.batch else None

    def update(self, instance, validated_data):
        validated_data.pop('email', None)
        image = validated_data.pop('image', None)
        if image:
            instance.image = image

        # Update other fields of Student
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def get_role(self, obj):
        return ROLE_MAP.get(obj.user.role, -1)

    def get_imageUrl(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else settings.MEDIA_URL + obj.image.url
        return None

class TeacherSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    role = serializers.SerializerMethodField()
    imageUrl = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False)
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
            'image',
            "role",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "role", "user"]

    def get_role(self, obj):
        return ROLE_MAP.get(obj.user.role, -1)
    def get_imageUrl(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else settings.MEDIA_URL + obj.image.url
        return None