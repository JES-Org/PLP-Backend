from django.urls import path
from .views import (
    ClassroomView,
    TeacherClassroomView,
    StudentClassroomView,
    AddBatchView,
    SearchClassroomView,
    AddStudentView,
    RemoveStudentView,
)

urlpatterns = [
    path('', ClassroomView.as_view(), name='classroom-list-create-update'),
    path('<int:id>/', ClassroomView.as_view(), name='classroom-detail'),
    path('teacher/<int:teacher_id>/', TeacherClassroomView.as_view(), name='classroom-by-teacher'),
    path('student/<int:student_id>/', StudentClassroomView.as_view(), name='classroom-by-student'),
    path('add-batch/', AddBatchView.as_view(), name='classroom-add-batch'),
    path('search/', SearchClassroomView.as_view(), name='classroom-search'),
    path('add-student/', AddStudentView.as_view(), name='classroom-add-student'),
    path('remove-student/', RemoveStudentView.as_view(), name='classroom-remove-student'),
]