from django.urls import path
from .views import AddQuestionView, AssessmentListCreateView, AssessmentDetailView, AssessmentPublishView

urlpatterns = [
    path('', AssessmentListCreateView.as_view(), name='list-create-assessment'),
    path('publish/<int:id>/', AssessmentPublishView.as_view(), name='publish-assessment'),
    path('<int:id>/', AssessmentDetailView.as_view(), name='get-assessment'),
    path('add-question/', AddQuestionView.as_view(), name='add-question'),
]