from django.urls import path
from .views import AddQuestionView, AddSubmissionView, AssessmentListCreateView, AssessmentDetailView, AssessmentPublishView, GetSubmissionByStudentAndAssessmentView

urlpatterns = [
    path('', AssessmentListCreateView.as_view(), name='list-create-assessment'),
    path('publish/<int:id>/', AssessmentPublishView.as_view(), name='publish-assessment'),
    path('<int:id>/', AssessmentDetailView.as_view(), name='get-assessment'),
    path('add-question/', AddQuestionView.as_view(), name='add-question'),
    path('add-submission/', AddSubmissionView.as_view(), name='add-submission'),
    path('submission/student/<int:student_id>/assessment/<int:assessment_id>/', GetSubmissionByStudentAndAssessmentView.as_view(), name='get-submission-by-student'),
]