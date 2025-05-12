from django.urls import path
from .views import AssessmentCreateView, AssessmentPublishView

urlpatterns = [
    path('classroom/<str:classroom_id>/assessment/', AssessmentCreateView.as_view(), name='create-assessment'),
    path('classroom/<str:classroom_id>/assessment/publish/<str:id>/', AssessmentPublishView.as_view(), name='publish-assessment'),
]