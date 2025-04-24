from django.contrib import admin
from .models import User, Teacher, Student
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "role", "is_active", "is_staff")
    list_filter = ("role", "is_staff")
    ordering = ("email",)
    search_fields = (
        "email",
        "username",
    )
    fieldsets = (
        (None, {"fields": ("email", "password", "username", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Groups", {"fields": ("groups", "user_permissions")}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Teacher)
admin.site.register(Student)
