from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import LearningPath, ChatHistory
from .utils.ai_utils import SessionManager
from .utils.prompts import GREETING_PROMPT, DETAIL_TEMPLATE, GENERATE_TEMPLATE
from langchain.prompts import ChatPromptTemplate
from .serializers import ChatHistorySerializer, LearningPathSerializer


class HealthCheckView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"isSuccess": True, "aiResponse": "Stayin' Alive oh oh oh!"})

class RestartSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.data.get("studentId")
            SessionManager.clear_session(user_id)
            return Response({"isSuccess": True, "aiResponse": "Memory is cleared!"})
        except Exception as e:
            return Response({"isSuccess": False, "error": str(e)}, status=500)

class GreetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.data.get("studentId")
            session = SessionManager.get_session(user_id)
            llm, _ = session["llm"]
            greeting_response = llm.predict(input=GREETING_PROMPT)

            ChatHistory.objects.create(
                user=request.user,
                message=greeting_response,
                is_ai_response=True
            )

            return Response({"isSuccess": True, "aiResponse": greeting_response})
        
        except Exception as e:
            print(f"Error in GreetView: {e}")

            return Response({"isSuccess": False, "error": str(e)}, status=500)

class DetailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.data.get("studentId")
            student_prompt = request.data.get("studentResponse")

            ChatHistory.objects.create(
                user=request.user,
                message=student_prompt,
                is_ai_response=False
            )

            session = SessionManager.get_session(user_id)
            llm, _ = session["llm"]
            prompt_template = ChatPromptTemplate.from_template(DETAIL_TEMPLATE)
            cooked_prompt = prompt_template.format_messages(student_prompt=student_prompt)
            response = llm.predict(input=cooked_prompt[0].content)

            ChatHistory.objects.create(
                user=request.user,
                message=response,
                is_ai_response=True
            )

            return Response({"isSuccess": True, "aiResponse": response})
        except Exception as e:
            return Response({"isSuccess": False, "error": str(e)}, status=500)

class GeneratePathView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.data.get("studentId")
            student_answers = request.data.get("studentResponse")

            ChatHistory.objects.create(
                user=request.user,
                message=student_answers,
                is_ai_response=False
            )

            session = SessionManager.get_session(user_id)
            llm, _ = session["llm"]
            prompt_template = ChatPromptTemplate.from_template(GENERATE_TEMPLATE)
            cooked_prompt = prompt_template.format_messages(student_answers=student_answers)
            response = llm.predict(input=cooked_prompt[0].content)

            ChatHistory.objects.create(
                user=request.user,
                message=response,
                is_ai_response=True
            )

            return Response({"isSuccess": True, "aiResponse": response})
        except Exception as e:
            return Response({"isSuccess": False, "error": str(e)}, status=500)

class SavePathView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("incomming data", request.data)
        try:
            title = request.data.get("learningPathTitle")
            last_response = ChatHistory.objects.filter(user=request.user, is_ai_response=True).order_by('-created_at').first()
            print("last response", last_response)


            if not last_response:
                return Response({"isSuccess": False, "error": "No chat history to save"}, status=400)

            LearningPath.objects.create(
                student=request.user,
                title=title,
                content=last_response.message
            )

            return Response({"isSuccess": True, "aiResponse": "Your learning path is saved, Be sure to follow it!"})
        except Exception as e:
            print(f"Error in SavePathView: {e}")
            return Response({"isSuccess": False, "error": str(e)}, status=500)


class GetPathsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            paths = LearningPath.objects.filter(student=request.user)
            serializer = LearningPathSerializer(paths, many=True)
            return Response({"isSuccess": True, "learningPaths": serializer.data})
        except Exception as e:
            return Response({"isSuccess": False, "error": str(e)}, status=500)
class GetPathView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            path = get_object_or_404(LearningPath, id=pk, student=request.user)
            return Response({
                "isSuccess": True,
                "learningPath": {
                    "learningPathId": path.id,
                    "learningPathTitle": path.title,
                    "content": path.content,
                    "createdAt": path.created_at
                }
            })
        except Exception as e:
            return Response({"isSuccess": False, "error": str(e)}, status=500)


class DeletePathView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            path = get_object_or_404(LearningPath, id=pk, student=request.user)
            path.delete()
            return Response({"isSuccess": True, "aiResponse": "Learning path deleted!"})
        except Exception as e:
            return Response({"isSuccess": False, "error": str(e)}, status=500)

class MarkPathCompletedView(APIView):
    def put(self, request, pk):
        print("incomming data", request.data)
        student_id = request.data.get('studentId')
        try:
            learning_path = LearningPath.objects.get(pk=pk, student_id=student_id)
            learning_path.isCompleted = True
            learning_path.save()
        except Exception as e:
            return Response({"isSuccess": False, "error": str(e)}, status=500)
        return Response({"isSuccess": True, "message": "Learning path delemark as completed !"})
        


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.query_params.get("studentId")
        if not student_id:
            return Response({"isSuccess": False, "error": "studentId parameter is required"}, status=400)
        if str(request.user.id) != student_id:
            return Response({"isSuccess": False, "error": "Unauthorized"}, status=403)
        history = ChatHistory.objects.filter(user=request.user).order_by("created_at")
        serializer = ChatHistorySerializer(history, many=True)
        return Response({"isSuccess": True, "chatHistory": serializer.data})
