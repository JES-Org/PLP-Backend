from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Department,
    Batch,
    Classroom,
    Announcement,
    Attachment,
    Message,
)
from users.models import Teacher, Student

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
            "department",
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
            source="teacher",  # This maps creatorId to the model's teacher field
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
    announcement = serializers.PrimaryKeyRelatedField(
        queryset=Announcement.objects.all()
    )
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Attachment
        fields = ["id", "announcement", "file", "file_url"]
        extra_kwargs = {
            "file": {"write_only": True}
        }

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and hasattr(obj.file, "url"):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class AnnouncementSerializer(serializers.ModelSerializer):
    class_room = serializers.PrimaryKeyRelatedField(
        queryset=Classroom.objects.all()
    )
    class_room_details = ClassroomSerializer(
        source="class_room", read_only=True
    )
    batch = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.all(), required=False, allow_null=True
    )
    batch_details = BatchSerializer(source="batch", read_only=True)

    attachments = AttachmentSerializer(many=True, read_only=True)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "content",
            "class_room",
            "class_room_details",
            "batch",
            "batch_details",
            "attachments",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "fields"):
            if "class_room_details" in self.fields:
                self.fields["class_room"].write_only = True
            if "batch_details" in self.fields and self.fields.get("batch"): # batch can be null
                self.fields["batch"].write_only = True


class MessageParticipantSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(read_only=True) # 'teacher' or 'student'
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)

    def to_representation(self, instance):
        if isinstance(instance, Teacher):
            return {
                "id": instance.id,
                "type": "teacher",
                "full_name": f"{instance.first_name} {instance.last_name}",
                "email": instance.user.email,
            }
        elif isinstance(instance, Student):
            return {
                "id": instance.id,
                "type": "student",
                "full_name": f"{instance.first_name} {instance.last_name}",
                "email": instance.user.email,
            }
        return None


class MessageSerializer(serializers.ModelSerializer):
    sender_teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    sender_student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    receiver_teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    receiver_student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    sender = MessageParticipantSerializer(read_only=True)
    receiver = MessageParticipantSerializer(read_only=True)

    class_room = serializers.PrimaryKeyRelatedField(
        queryset=Classroom.objects.all()
    )
    class_room_details = ClassroomSerializer(
        source="class_room", read_only=True
    )

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "content",
            "class_room",
            "class_room_details",
            "sender_teacher",
            "sender_student",
            "receiver_teacher",
            "receiver_student",
            "sender",
            "receiver",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "fields") and "class_room_details" in self.fields:
            self.fields["class_room"].write_only = True


    def validate(self, data):
        instance = self.instance

        final_sender_teacher = data.get('sender_teacher', getattr(instance, 'sender_teacher', None))
        if 'sender_teacher' in data:
            final_sender_teacher = data['sender_teacher']

        final_sender_student = data.get('sender_student', getattr(instance, 'sender_student', None))
        if 'sender_student' in data:
            final_sender_student = data['sender_student']

        if bool(final_sender_teacher) == bool(final_sender_student):
            error_msg = "Specify exactly one sender (teacher or student)."
            if not final_sender_teacher and not final_sender_student:
                error_msg = "A sender (teacher or student) must be specified."
           
            raise serializers.ValidationError({
                "sender_teacher": error_msg,
                "sender_student": error_msg,
            })

        final_receiver_teacher = data.get('receiver_teacher', getattr(instance, 'receiver_teacher', None))
        if 'receiver_teacher' in data:
            final_receiver_teacher = data['receiver_teacher']

        final_receiver_student = data.get('receiver_student', getattr(instance, 'receiver_student', None))
        if 'receiver_student' in data:
            final_receiver_student = data['receiver_student']

        if bool(final_receiver_teacher) == bool(final_receiver_student):
            error_msg = "Specify exactly one receiver (teacher or student)."
            if not final_receiver_teacher and not final_receiver_student:
                error_msg = "A receiver (teacher or student) must be specified."
            raise serializers.ValidationError({
                "receiver_teacher": error_msg,
                "receiver_student": error_msg,
            })

        return data

