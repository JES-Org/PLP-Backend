from rest_framework import serializers

from users.models import Teacher
from .models import Classroom, Announcement, Message
from users.serializers import UserSerializer


class ClassroomSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    students = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Classroom
        fields = '__all__'


class AnnouncementSerializer(serializers.ModelSerializer):
    class_room = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all())

    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ['created_at']


class MessageSerializer(serializers.ModelSerializer):
    class_room = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all())
    sender = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['created_at']
