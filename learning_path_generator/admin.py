from django.contrib import admin
from .models import LearningPath, ChatHistory,Task

# @admin.register(LearningPath)
# class LearningPathAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'created_at','updated_at')
# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'description','category','week_number','day_range')
# @admin.register(ChatHistory)
# class ChatHistoryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'message',"is_ai_response",'created_at')
#     list_filter = ('created_at',)
#     ordering = ('-created_at',)
#     date_hierarchy = 'created_at'
#     list_per_page = 20
#     list_display_links = ('id', 'user')




