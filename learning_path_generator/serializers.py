from rest_framework import serializers
from .models import ChatHistory, LearningPath

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = '__all__'

class LearningPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPath
        fields = ['id', 'title', 'content','deadline', 'isCompleted','created_at']
