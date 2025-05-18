from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import ForumMessage
from .serializers import ForumMessageSerializer
from classrooms.models import Classroom
from utlits.response import success_response, error_response
class ForumMessageListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, classroom_id):
        try:
            messages = ForumMessage.objects.filter(classroom_id=classroom_id).order_by('updatedAt')
            serializer = ForumMessageSerializer(messages, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            return error_response(errors=[str(e)])

    def post(self, request, classroom_id):
        try:
            classroom = Classroom.objects.get(id=classroom_id)
            serializer = ForumMessageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(sender=request.user, classroom=classroom)
                return success_response(
                    data=serializer.data,
                    message="Message created successfully.",
                    status_code=status.HTTP_201_CREATED
                )
            return error_response(message="Validation error", errors=serializer.errors)
        
        except Classroom.DoesNotExist:
            return error_response(message="Classroom not found", errors=["Invalid classroomId"], status_code=404)
        except Exception as e:
            return error_response(errors=[str(e)])


class ForumMessageUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, classroom_id):
        try:
            message_id = request.data.get("id")
            if not message_id:
                return error_response(message="Missing messageId", errors=["messageId required"], status_code=400)

            message = ForumMessage.objects.get(pk=message_id, classroom_id=classroom_id)

            if message.sender != request.user:
                return error_response(message="Unauthorized", errors=["Permission denied"], status_code=403)

            message.content = request.data.get('content')
            message.save()
            serializer = ForumMessageSerializer(message)
            return success_response(data=serializer.data, message="Message updated successfully.")
        except ForumMessage.DoesNotExist:
            return error_response(message="Message not found", errors=["Invalid ID"], status_code=404)
        except Exception as e:
            return error_response(errors=[str(e)])


class ForumMessageDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, classroom_id):

        try:
            message_id = request.query_params.get("messageId")

            if not message_id:
                return error_response(message="Missing messageId", errors=["messageId required"], status_code=400)

            message = ForumMessage.objects.get(pk=message_id, classroom_id=classroom_id)
            if message.sender != request.user:
                return error_response(message="Unauthorized", errors=["Permission denied"], status_code=403)

            message.delete()
            return success_response(message="Message deleted successfully.")
        except ForumMessage.DoesNotExist:
            return error_response(message="Message not found", errors=["Invalid ID"], status_code=404)
        except Exception as e:
            return error_response(errors=[str(e)])
