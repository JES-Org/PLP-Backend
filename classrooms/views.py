from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Classroom, Teacher, Student, Batch,Department
from .serializers import ClassroomSerializer,DepartmentSerializer
 

class ClassroomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None):
        try:
            if id:
                classroom = get_object_or_404(Classroom, id=id)
                serializer = ClassroomSerializer(classroom)
                return Response({
                    "isSuccess": True,
                    "message": None,
                    "data": serializer.data,
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
        student_id = request.query_params.get('studentId')
        classroom_id = request.query_params.get('classroomId')
        classroom = get_object_or_404(Classroom, id=classroom_id)
        student = get_object_or_404(Student, id=student_id)
        for batch in classroom.batches.all():
            batch.students.add(student)
        # Optionally publish event here
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