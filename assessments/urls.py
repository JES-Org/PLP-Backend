from django.urls import path
from .views import (AddQuestionView, AddSubmissionView, AssessmentAnalyticsByTagView, 
                    AssessmentAnalyticsView, AssessmentListCreateView, 
                    AssessmentDetailView, AssessmentPublishView, 
                    CrossAssessmentAnalyticsView, DeleteQuestionView, 
                    GetSubmissionByStudentAndAssessmentView, 
                    GradeStudentsView,AssessmentUnpublishView,
                    AgregateAssessmentAnalyticsView
                    )

urlpatterns = [
    path('', AssessmentListCreateView.as_view(), name='list-create-assessment'),
    path('publish/<int:id>/', AssessmentPublishView.as_view(), name='publish-assessment'),
    path('unpublish/<int:id>/', AssessmentUnpublishView.as_view(), name='unpublish-assessment'),
    path('<int:id>/', AssessmentDetailView.as_view(), name='get-assessment'),
    path('add-question/', AddQuestionView.as_view(), name='add-question'),
    path('question/<int:question_id>/', DeleteQuestionView.as_view(), name='delete-question'),
    path('add-submission/', AddSubmissionView.as_view(), name='add-submission'),
    path('submission/student/<int:student_id>/assessment/<int:assessment_id>/', GetSubmissionByStudentAndAssessmentView.as_view(), name='get-submission-by-student'),
    path('analytics/<int:assessment_id>/', AssessmentAnalyticsView.as_view(), name='single-assessment-analytics'),
    path('analytics/cross-assessment/', CrossAssessmentAnalyticsView.as_view(), name='cross-assessment-analytics'),
    path('analytics/', AssessmentAnalyticsByTagView.as_view(), name='analytics-by-tag'),
    path('analytics/agregate/', AgregateAssessmentAnalyticsView.as_view(), name='agregate-assessment-analytics'),
    path('analytics/grade/', GradeStudentsView.as_view(), name='grade-students'),
]