from django.contrib import admin
from .models import Classroom,Department,Batch


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'teacher', 'description', 'courseNo',"get_batches")
    search_fields = ('name',)
    ordering = ('-id',)
    list_per_page = 10
    list_display_links = ('id', 'name')
    def get_batches(self, obj):
        return ", ".join([str(batch) for batch in obj.batches.all()])
    get_batches.short_description = 'Batches'    


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    ordering = ('-id',)
    list_per_page = 10
    list_display_links = ('id', 'name')



@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'section', 'year', 'department')
    search_fields = ('section',)
    ordering = ('-id',)
    list_per_page = 10
    list_display_links = ('id', 'section')
