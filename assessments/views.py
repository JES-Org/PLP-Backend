from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from classrooms.models import Classroom
from .models import Assessment
from .serializers import AssessmentSerializer

class AssessmentCreateView(generics.CreateAPIView):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        classroom_id = self.kwargs.get('classroom_id')
        data = request.data.copy()
        data['classroom'] = classroom_id

        try:
            Classroom.objects.get(id=classroom_id)
        except Classroom.DoesNotExist:
            return Response({
                "isSuccess": False,
                "message": "Assessment could not be created",
                "data": None,
                "errors": ["Classroom does not exist."]
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "isSuccess": True,
            "message": "Assessment created successfully.",
            "data": serializer.data,
            "errors": []
        }, status=status.HTTP_201_CREATED)
