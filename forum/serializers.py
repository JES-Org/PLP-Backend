# serializers.py
from rest_framework import serializers
from .models import ForumMessage
from django.contrib.auth import get_user_model
from users.serializers import UserProfileSerializer

User = get_user_model()


class ForumMessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)
    class Meta:
        model = ForumMessage
        fields = '__all__'
        read_only_fields = ['classroom', 'sender', 'created_at', 'updatedAt']