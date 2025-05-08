# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import UnreadNotificationSerializer, NotificationSerializer

class UnreadNotificationsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        class_room_id = request.query_params.get('classRoomId')
        if not class_room_id:
            return Response(
                {"error": "classRoomId parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        notifications = Notification.objects.filter(
            classroom_id=class_room_id,
            is_read=False
        ).order_by('-created_at')

        serializer = UnreadNotificationSerializer(notifications, many=True)
        
        response_data = {
            "isSuccess": True,
            "message": "Unread notifications retrieved successfully",
            "data": serializer.data,
            "errors": None
        }
        return Response(response_data)

class NotificationDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, notification_id):
        class_room_id = request.query_params.get('classRoomId')
        if not class_room_id:
            return Response(
                {"error": "classRoomId parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        notification = get_object_or_404(
            Notification,
            id=notification_id,
            classroom_id=class_room_id
        )

        # Mark as read when fetched
        notification.is_read = True
        notification.save()

        serializer = NotificationSerializer(notification)
        
        response_data = {
            "isSuccess": True,
            "message": "Notification retrieved successfully",
            "data": serializer.data,
            "errors": None
        }
        return Response(response_data)
