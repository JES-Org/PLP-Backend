from django.contrib import admin
from .models import LearningPath, ChatHistory





@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'isCompleted','updated_at')
    search_fields = ('title',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    list_display_links = ('id', 'title')


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message',"is_ai_response",'created_at')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    list_display_links = ('id', 'user')


