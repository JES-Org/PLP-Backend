from django.contrib import admin
from .models import Classroom,Department,Batch,Announcement,Attachment,Faculty
admin.site.index_title = "Welcome to Your Project Dashboard"

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.contrib.auth.models import User, Group, Permission

admin.site.unregister(Group)
admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'teacher', 'courseNo',"get_batches")
    search_fields = ('name',)
    ordering = ('-id',)
    list_per_page = 10
    list_display_links = ('id', 'name')
    def get_batches(self, obj):
        return ", ".join([str(batch) for batch in obj.batches.all()])
    get_batches.short_description = 'Batches'    


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('department', 'year', 'section')
    list_filter = ('department', 'year')
    search_fields = ('section', 'department__name')
    autocomplete_fields = ['department']
    ordering = ('-year', 'department', 'section')
    list_per_page = 25
    actions = ['duplicate_batch']

    def duplicate_batch(self, request, queryset):
        count = 0
        for batch in queryset:
            new_year = batch.year + 1
            if not Batch.objects.filter(
                section=batch.section,
                year=new_year,
                department=batch.department
            ).exists():
                Batch.objects.create(
                    section=batch.section,
                    year=new_year,
                    department=batch.department
                )
                count += 1
        self.message_user(request, f"✅ {count} batch(es) duplicated to the next academic year.")
    
    duplicate_batch.short_description = "➕ Duplicate selected batches to next year"


# @admin.register(Announcement)
# class AnnouncementAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title','content','class_room', 'created_at')
#     search_fields = ('title',)
#     ordering = ('-id',)
#     list_per_page = 10
#     list_display_links = ('id', 'title')

# @admin.register(Attachment)
# class AttachmentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'file', 'announcement', 'created_at')
#     search_fields = ('file',)
#     ordering = ('-id',)
#     list_display_links = ('id', 'file')




@admin.register(Faculty)
class FuclityAdmin(admin.ModelAdmin):
      list_display =('id','name')


