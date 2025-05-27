from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from django.contrib.auth import authenticate

from .models import User, Teacher, Student
from django.conf import settings
from classrooms.models import Batch
from classrooms.serializers import BatchSerializer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
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

    def validate_email(self, value):
    
        # First validate basic email format
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        
        # Check for bdu domain
        if not re.match(r'^[a-zA-Z0-9_.+-]+@bdu\.edu\.et$', value):
            raise serializers.ValidationError("Email must be a valid @bdu.edu.et address.")
        
        return value

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
    
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        profile_is_verified = False
        profile_exists = False

        if user.role == "student":
            if hasattr(user, 'student_profile'):
                profile_exists = True
                profile_is_verified = user.student_profile.is_verified
            else:
                print(f"Warning: Student user {user.email} has no student_profile during login.")
        elif user.role == "teacher":
            if hasattr(user, 'teacher_profile'):
                profile_exists = True
                profile_is_verified = user.teacher_profile.is_verified
            else:
                print(f"Warning: Teacher user {user.email} has no teacher_profile during login.")

        if not profile_exists and user.role in ["student", "teacher"]:
            raise AuthenticationFailed(
                detail='User profile not found. Please contact support.',
                code='profile_missing'
            )

        if not profile_is_verified:
            raise AuthenticationFailed(
                detail='Account not verified. Please check your email for OTP and verify your account.',
                code='account_not_verified'
            )

        return data

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
            "dob", "phone", "batch", "batch_details",
            "department", "section", "year",  
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
            "faculty",
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


class UserProfileSerializer(serializers.ModelSerializer):
    firstName = serializers.SerializerMethodField()
    lastName = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active', 'is_staff', 'firstName', 'lastName']

    def get_firstName(self, obj):
        if obj.role == 'student' and hasattr(obj, 'student_profile'):
            return obj.student_profile.first_name
        elif obj.role == 'teacher' and hasattr(obj, 'teacher_profile'):
            return obj.teacher_profile.first_name
        return None

    def get_lastName(self, obj):
        if obj.role == 'student' and hasattr(obj, 'student_profile'):
            return obj.student_profile.last_name
        elif obj.role == 'teacher' and hasattr(obj, 'teacher_profile'):
            return obj.teacher_profile.last_name
        return None       