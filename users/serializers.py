from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import authenticate

from .models import User, Teacher, Student

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "role"]

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    dob = serializers.DateField(write_only=True)
    phone = serializers.CharField(write_only=True)
    department = serializers.CharField(write_only=True)
    student_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'role',
            'first_name', 'last_name', 'dob', 'phone', 'department', 'student_id'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role = validated_data['role']
        student_id = validated_data.pop('student_id', None)
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        dob = validated_data.pop('dob')
        phone = validated_data.pop('phone')
        department = validated_data.pop('department')

        user = User.objects.create_user(**validated_data)

        if role == 'teacher':
            Teacher.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                dob=dob,
                phone=phone,
                department=department
            )
        elif role == 'student':
            Student.objects.create(
                user=user,
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                dob=dob,
                phone=phone,
                department=department
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
        token['role'] = user.role
        token['username'] = user.username
        return token

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'
        read_only_fields = ['user']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['user']