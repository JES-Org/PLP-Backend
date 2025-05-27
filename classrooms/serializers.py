from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Department,
    Batch,
    Classroom,
    Announcement,
    Attachment,
    Message,
    Faculty,
)
from users.models import Teacher, Student,User


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = "__all__"
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']        

class TeacherInlineSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            "id",
            "user_email",
            "full_name",
            "first_name",
            "last_name",
            "faculty",
        ]
        read_only_fields = ["first_name", "last_name"]


    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class StudentInlineSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    batch_details = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "user_email",
            "full_name",
            "first_name",
            "last_name",
            "student_id",
            "department", 
            "batch_details"  
        ]
        read_only_fields = ["first_name", "last_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_department(self, obj):
        return obj.batch.department.name if obj.batch else None

    def get_batch_details(self, obj):
        if obj.batch:
            return {
                "id": obj.batch.id,
                "section": obj.batch.section,
                "year": obj.batch.year
            }
        return None



class BatchSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all()
    )
    department_details = DepartmentSerializer(
        source="department", read_only=True
    )
    students = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True 
    )
    student_details = StudentInlineSerializer(
        source="students", 
        many=True, 
        read_only=True
    )

    class Meta:
        model = Batch
        fields = [
            "id",
            "section",
            "year",
            "department",
            "department_details",
            "students",
            "student_details",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "fields"):
            if "department_details" in self.fields:
                self.fields["department"].write_only = True

class ClassroomSerializer(serializers.ModelSerializer):
    creatorId = serializers.PrimaryKeyRelatedField(
            queryset=Teacher.objects.all(),
            source="teacher",
            write_only=True
        )
    teacher_details = TeacherInlineSerializer(source="teacher", read_only=True)
    batches = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.all(), many=True, required=False
    )
    batch_details = BatchSerializer(source="batches", many=True, read_only=True)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Classroom
        fields = [
            "id",
            "name",
            "courseNo",
            "description",
            "creatorId",
            "teacher_details",
            "batches",
            "batch_details",
            "is_archived",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "fields"):
            if "teacher_details" in self.fields:
                self.fields["creatorId"].write_only = True
            if "batch_details" in self.fields:
                self.fields["batches"].write_only = True


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file']
        read_only_fields = ['id']

class AnnouncementSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    class_room_details = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            'id', 
            'title', 
            'content', 
            'class_room', 
            'class_room_details',
            'attachments',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'attachments']
        extra_kwargs = {
            'class_room': {'write_only': True}
        }

    def get_class_room_details(self, obj):
        from classrooms.serializers import ClassroomSerializer
        return ClassroomSerializer(obj.class_room).data


class MessageSenderSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'display_name'] # Add other fields if needed like 'email'

    def get_display_name(self, user_obj):
        # Logic to get display name (similar to your consumer)
        # Ensure your User model has a 'role' attribute or adapt this logic
        if hasattr(user_obj, 'role'):
            if user_obj.role == 'teacher':
                teacher = Teacher.objects.filter(user=user_obj).first()
                if teacher:
                    return f"{teacher.first_name} {teacher.last_name}"
            elif user_obj.role == 'student':
                student = Student.objects.filter(user=user_obj).first()
                if student:
                    return f"{student.first_name} {student.last_name}"
        return user_obj.email # Fallback or primary if no role/profile

class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'content', 'sender_id', 'sender_name', 'timestamp']
    

    def get_sender_name(self, message_obj):
        user_obj = message_obj.sender
       
        if hasattr(user_obj, 'role'):
            if user_obj.role == 'teacher':
                teacher = Teacher.objects.filter(user=user_obj).first()
                if teacher:
                    return f"{teacher.first_name} {teacher.last_name}"
            elif user_obj.role == 'student':
                student = Student.objects.filter(user=user_obj).first()
                if student:
                    return f"{student.first_name} {student.last_name}"
        return user_obj.email 