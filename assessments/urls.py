from django.urls import path
from .views import AssessmentCreateView

urlpatterns = [
    path('classroom/<str:classroom_id>/assessment/', AssessmentCreateView.as_view(), name='create-assessment'),
]