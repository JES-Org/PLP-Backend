from rest_framework import serializers
from .models import ChatHistory, LearningPath,Task

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = '__all__'

# class LearningPathSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LearningPath
#         fields = ['id', 'title', 'content','deadline', 'isCompleted','created_at']





class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'category','week_title','is_completed', "day_range",'day_range','order']

class LearningPathsSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    completion_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = LearningPath
        fields = ['id', 'title','deadline', 'tasks', 'completion_percentage']
