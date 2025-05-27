from django.contrib import admin,messages
from .models import User, Teacher, Student
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from classrooms.models import Batch

class UserAdmin(BaseUserAdmin):
    list_display = ("email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_staff")
    ordering = ("email",)
    search_fields = (
        "email",
    )
    fieldsets = (
        (None, {"fields": ("email", "password", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Groups", {"fields": ("groups", "user_permissions")}),
    )
    list_per_page=25


admin.site.register(User, UserAdmin)
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'faculty', 'is_verified', 'created_at')
    list_filter = ('faculty', 'is_verified', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone', 'user__username')
    autocomplete_fields = ['user']
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25

class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'batch', 'phone','academic_status')
    list_filter = ('batch','academic_status',)  
    search_fields = ('student_id', 'first_name', 'last_name')
    actions = ['promote_students']
    autocomplete_fields = ['batch']  
    list_per_page = 25



    @admin.action(description="Promote selected students to next academic year")
    def promote_students(self, request, queryset):
       
        promoted = 0
        skipped = 0
        errors = 0
        for student in queryset:
            if student.academic_status != 'active':
                skipped += 1
                continue

            current_batch = student.batch
            if not current_batch:
                errors += 1
                continue

            # Determine the next year batch
            next_year = current_batch.year + 1
            try:
                next_batch = Batch.objects.get(
                    section=current_batch.section,
                    department=current_batch.department,
                    year=next_year
                )
            except Batch.DoesNotExist:
                next_batch = Batch.objects.create(
                    section=current_batch.section,
                    department=current_batch.department,
                    year=next_year
                )

            student.batch = next_batch
            student.save()
            promoted += 1

        if promoted:
            self.message_user(request, f"✅ Successfully promoted {promoted} active student(s).", messages.SUCCESS)
        if skipped:
            self.message_user(request, f"⚠️ Skipped {skipped} student(s) not marked as active.", messages.WARNING)
        if errors:
            self.message_user(request, f"⚠️ Skipped {errors} student(s) without an assigned batch.", messages.ERROR)

admin.site.register(Student, StudentAdmin)
