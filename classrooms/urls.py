from django.urls import path
from .views import (
    ClassroomView,
    TeacherClassroomView,
    StudentClassroomView,
    AddBatchView,
    SearchClassroomView,
    AddStudentView,
    RemoveStudentView,
    DepartmentListCreateView,
    DepartmentDetailView,
    AnnouncementListCreateView,
    AnnouncementDetailView,
    AttachmentView,
    AttachmentDownloadView,


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
    path('department/', DepartmentListCreateView.as_view(), name='department-list-create'), 
    path('department/<int:id>/', DepartmentDetailView.as_view(), name='department-detail'),
    path('<int:class_room_id>/announcements/', AnnouncementListCreateView.as_view(), name='announcement-list-create'),
    path('<int:class_room_id>/announcements/<int:id>/', AnnouncementDetailView.as_view(), name='announcement-detail'),
    path('<int:class_room_id>/announcements/attach/<int:id>/', AttachmentView.as_view(), name='attachment-create'),
    path('<int:class_room_id>/announcements/<int:id>/attachments/<int:attachment_id>/', AttachmentDownloadView.as_view(), name='attachment-download'),
    
]