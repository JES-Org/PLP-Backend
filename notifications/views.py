from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer


class UnreadNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        unread_notifications = Notification.objects.filter(recipient=user, is_read=False)
        serializer = NotificationSerializer(unread_notifications, many=True)

        return Response({
            "isSuccess": True,
            "message": "Unread notifications retrieved",
            "data": serializer.data,
            "errors": None
        })


class MarkNotificationAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, recipient=request.user)
            notification.is_read = True
            notification.save()

            return Response({
                "isSuccess": True,
                "message": "Notification marked as read",
                "data": None,
                "errors": None
            })
        except Notification.DoesNotExist:
            return Response({
                "isSuccess": False,
                "message": "Notification not found",
                "data": None,
                "errors": "Notification with given ID does not exist or doesn't belong to you."
            }, status=status.HTTP_404_NOT_FOUND)
