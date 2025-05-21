from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Classroom, Teacher, Student, Batch,Department, Announcement, Attachment,Message
from .serializers import ClassroomSerializer,DepartmentSerializer, AnnouncementSerializer, AttachmentSerializer,MessageSerializer
from django.http import FileResponse
import os
from rest_framework.views import exception_handler
import mimetypes

class ClassroomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None):
        try:
            if id:
                classroom = get_object_or_404(Classroom, id=id)
                serializer = ClassroomSerializer(classroom)
                data = serializer.data
                data['members'] = []
                for batch in classroom.batches.all():
                    data['members'].extend(batch.students.values())
                return Response({
                    "isSuccess": True,
                    "message": None,
                    "data": data,
                    "errors": None
                })
            else:
                classrooms = Classroom.objects.all()
                serializer = ClassroomSerializer(classrooms, many=True)
                Response({
                    "isSuccess": True,
                    "message": None,
                    "data": serializer.data,
                    "errors": None
                })
        except Exception as e:
           return Response({
            "isSuccess": False,
            "message": "An error occurred.",
            "data": None,
            "errors": [str(e)]
        }, status=status.HTTP_400_BAD_REQUEST)       

    def post(self, request):
        serializer = ClassroomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # PUT /api/classroom/ (update)
        classroom_id = request.data.get('id')
        classroom = get_object_or_404(Classroom, id=classroom_id)
        serializer = ClassroomSerializer(classroom, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Optionally publish event here
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id=None):
        # DELETE /api/classroom/{id}
        classroom = get_object_or_404(Classroom, id=id)
        classroom.delete()
        # Optionally publish event here
        return Response(status=status.HTTP_204_NO_CONTENT)

class TeacherClassroomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, teacher_id):
        try:
            classrooms = Classroom.objects.filter(teacher__id=teacher_id)
            serializer = ClassroomSerializer(classrooms, many=True)
            return Response({
                "isSuccess": True,
                "message": None,
                "data": serializer.data,
                "errors": None
                })
        except Exception as e:
            return Response({
                "isSuccess": False,
                "message": "An error occurred.",
                "data": None,
                "errors": [str(e)]
            }, status=status.HTTP_400_BAD_REQUEST)
class StudentClassroomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):
        try:
            classrooms = Classroom.objects.filter(batches__students__id=student_id).distinct()
            serializer = ClassroomSerializer(classrooms, many=True)
            return Response({
                "isSuccess": True,
                "message": None,
                "data": serializer.data,
                "errors": None
            })
        except Exception as e:
            return Response({
                "isSuccess": False,
                "message": "An error occurred.",
                "data": None,
                "errors": [str(e)]
            }, status=status.HTTP_400_BAD_REQUEST)  

class AddBatchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        section = request.data.get('section')
        year = request.data.get('year')
        department = request.data.get('department')
        class_room_id = request.data.get('classRoomId')

        classroom = get_object_or_404(Classroom, id=class_room_id)
        batch, created = Batch.objects.get_or_create(
            section=section,
            year=year,
            department_id=department
        )
        classroom.batches.add(batch)
        classroom.save()
        return Response({'detail': 'Batch added successfully.'})


class SearchClassroomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:  
            query = request.query_params.get('query', '')
            classrooms = Classroom.objects.filter(
                Q(name__icontains=query) | Q(course_no__icontains=query)
            )
            serializer = ClassroomSerializer(classrooms, many=True)
            return Response({
                "isSuccess": True,
                "message": None,
                "data": serializer.data,
                "errors": None
            })
        except Exception as e:
            return Response({
                "isSuccess": False,
                "message": "An error occurred.",
                "data": None,
                "errors": [str(e)]
            }, status=status.HTTP_400_BAD_REQUEST)

class AddStudentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        print(request.data)
        rqbatch = request.data.get('batch')
        batch = Batch.objects.filter(year=rqbatch['year'], section=rqbatch['section'], department=rqbatch['department']).first()
        print(batch)
        students = Student.objects.filter(batch=batch)
        print(students)
        classroom_id = request.data.get('classRoomId')
        print(classroom_id)
        classroom = get_object_or_404(Classroom, id=classroom_id)
        print(classroom)
        
        for student in students:
            classroom.students.add(student)
        
        return Response({'detail': 'Student added successfully.'})

class RemoveStudentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        student_id = request.query_params.get('studentId')
        classroom_id = request.query_params.get('classroomId')
        classroom = get_object_or_404(Classroom, id=classroom_id)
        student = get_object_or_404(Student, id=student_id)
        for batch in classroom.batches.all():
            batch.students.remove(student)
        # Optionally publish event here
        return Response({'detail': 'Student removed successfully.'})
    
class DepartmentListCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DepartmentDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        department = get_object_or_404(Department, id=id)
        serializer = DepartmentSerializer(department)
        return Response(serializer.data)

    def put(self, request, id):
        department = get_object_or_404(Department, id=id)
        serializer = DepartmentSerializer(department, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        department = get_object_or_404(Department, id=id)
        department.delete()
        return Response({'success': True, 'id': id}, status=status.HTTP_200_OK)   
    
class AnnouncementListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, class_room_id):
        classroom = get_object_or_404(Classroom, id=class_room_id)
        announcements = Announcement.objects.filter(class_room=classroom).order_by('-created_at')
        serializer = AnnouncementSerializer(announcements, many=True)
        
        response_data = {
            "isSuccess": True,
            "message": "Announcements retrieved successfully",
            "data": serializer.data,
            "errors": None
        }
        return Response(response_data)

    def post(self, request, class_room_id):
        classroom = get_object_or_404(Classroom, id=class_room_id)
        data = request.data.copy()
        data['class_room'] = classroom.id
        
        serializer = AnnouncementSerializer(data=data)
        if serializer.is_valid():
            announcement = serializer.save()
            response_data = {
                "isSuccess": True,
                "message": "Announcement created successfully",
                "data": AnnouncementSerializer(announcement).data,
                "errors": None
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        response_data = {
            "isSuccess": False,
            "message": "Validation error",
            "data": None,
            "errors": serializer.errors
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

class AnnouncementDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, class_room_id, id):
        announcement = get_object_or_404(Announcement, id=id, class_room_id=class_room_id)
        serializer = AnnouncementSerializer(announcement)
        
        response_data = {
            "isSuccess": True,
            "message": "Announcement retrieved successfully",
            "data": serializer.data,
            "errors": None
        }
        return Response(response_data)

    def delete(self, request, class_room_id, id):
        announcement = get_object_or_404(Announcement, id=id, class_room_id=class_room_id)
        announcement.delete()
        
        response_data = {
            "isSuccess": True,
            "message": "Announcement deleted successfully",
            "data": None,
            "errors": None
        }
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)
    def put(self, request, class_room_id, id):
        announcement = get_object_or_404(Announcement, id=id, class_room_id=class_room_id)
        serializer = AnnouncementSerializer(announcement, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            response_data = {
                "isSuccess": True,
                "message": "Announcement updated successfully",
                "data": serializer.data,
                "errors": None
            }
            return Response(response_data)
        else:
            print(serializer.errors)
            response_data = {
                "isSuccess": False,
                "message": "Failed to update announcement",
                "data": None,
                "errors": serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST) 
    
class AttachmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, class_room_id, id):
        try:
            announcement = get_object_or_404(Announcement, id=id, class_room_id=class_room_id)
            print("request.FILES", request.FILES)

            if 'attachments' not in request.FILES:
                return Response({
                    "isSuccess": False,
                    "message": "No file provided",
                    "data": None,
                    "errors": ["No file provided"]
                }, status=status.HTTP_400_BAD_REQUEST)

            file = request.FILES['attachments']

            if file.size > 10 * 1024 * 1024:
                return Response({
                    "isSuccess": False,
                    "message": "File size exceeds 10MB limit",
                    "data": None,
                    "errors": ["File size exceeds 10MB limit"]
                }, status=status.HTTP_400_BAD_REQUEST)

            attachment = Attachment.objects.create(
                announcement=announcement,
                file=file
            )

            return Response({
                "isSuccess": True,
                "message": "Attachment created successfully",
                "data": AttachmentSerializer(attachment).data,
                "errors": None
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("Unexpected error:", str(e))
            return Response({
                "isSuccess": False,
                "message": "An unexpected error occurred",
                "data": None,
                "errors": [str(e)]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AttachmentDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, class_room_id, id, attachment_id):
        try:
            # Get the attachment
            announcement = get_object_or_404(Announcement, id=id, class_room_id=class_room_id)
            attachment = get_object_or_404(Attachment, id=attachment_id, announcement=announcement)

            if not attachment.file:
                return Response({
                    "isSuccess": False,
                    "message": "File not found",
                    "data": None,
                    "errors": ["File not found"]
                }, status=status.HTTP_404_NOT_FOUND)

            # Get the actual file object
            file_obj = attachment.file
            print(f"Original storage path: {file_obj.name}")  # Debug log

            # Safely extract filename with multiple fallbacks
            original_filename = "attachment"
            if file_obj.name:
                # Try to get the filename from the path
                try:
                    original_filename = os.path.basename(file_obj.name)
                except:
                    pass

                # If we got a path but no extension, try to find one
                if '.' not in original_filename:
                    try:
                        # For some storage backends, the name might include query params
                        original_filename = file_obj.name.split('?')[0].split('/')[-1]
                    except:
                        pass

            # If we still don't have a proper filename, use a default with ID
            if not original_filename or '.' not in original_filename:
                original_filename = f"attachment_{attachment.id}"

            # Get the file extension
            file_extension = os.path.splitext(original_filename)[1].lower()

            # Determine MIME type
            mime_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'

            # Special handling for common file types
            if file_extension == '.jpg' or file_extension == '.jpeg':
                mime_type = 'image/jpeg'
            elif file_extension == '.png':
                mime_type = 'image/png'
            elif file_extension == '.pdf':
                mime_type = 'application/pdf'
            elif file_extension == '.docx':
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif file_extension == '.xlsx':
                mime_type = 'application/vndxmlformats-officedocument.spreadsheetml.sheet'

            # Open the file
            try:
                file = file_obj.open('rb')
            except Exception as e:
                return Response({
                    "isSuccess": False,
                    "message": "Could not open file",
                    "data": None,
                    "errors": [str(e)]
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Create response
            response = FileResponse(file, content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{original_filename}"'
            response['Content-Length'] = file_obj.size

            return response

        except Exception as e:
            print(f"Error downloading file: {str(e)}")  # Debug log
            return Response({
                "isSuccess": False,
                "message": "An error occurred while downloading the file",
                "data": None,
                "errors": [str(e)]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttachmentDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, attachment_id):
        try:
     
            # Verify the attachment exists and belongs to the announcement
            attachment = get_object_or_404(
                Attachment, 
                id=attachment_id
            )
            
            # Delete the file from storage
            attachment.file.delete(save=False)
            # Delete the database record
            attachment.delete()
            
            return Response({
                "isSuccess": True,
                "message": "Attachment deleted successfully",
                "data": None,
                "errors": []
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "isSuccess": False,
                "message": "Failed to delete attachment",
                "data": None,
                "errors": [str(e)]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        

class ClassroomMessagesAPIView(APIView):
    """
    API endpoint to retrieve messages for a specific classroom.
    """
    permission_classes = [permissions.IsAuthenticated] 

    def get(self, request, classroom_id, format=None):
        try:
            classroom = Classroom.objects.get(id=classroom_id)
        except Classroom.DoesNotExist:
            return Response(
                {"error": "Classroom not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Optional: Check if the requesting user is part of this classroom
        # This depends on how you model classroom membership (e.g., a ManyToManyField on Classroom)
        # Example: if not classroom.participants.filter(id=request.user.id).exists():
        #     return Response(
        #         {"error": "You are not authorized to view messages for this classroom."},
        #         status=status.HTTP_403_FORBIDDEN
        #     )

        messages = Message.objects.filter(classroom=classroom).order_by('timestamp').select_related('sender')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)        