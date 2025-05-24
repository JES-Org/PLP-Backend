from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import LearningPath, ChatHistory,Task
from .utils.ai_utils import SessionManager
from .utils.prompts import GREETING_PROMPT, DETAIL_TEMPLATE, GENERATE_TEMPLATE
from langchain.prompts import ChatPromptTemplate
from .serializers import ChatHistorySerializer,LearningPathsSerializer
from .utils.contentParser import parse_learning_path_content
import re
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
            #insert the student prompt into the placeholder.
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
# Add this debugging function to your view
def print_content_sections(content):
    print("\n=== Content Analysis ===")
    
    # Find all week matches
    week_matches = re.finditer(r'\*\*Week (\d+):[^*]+\*\*\s*\*\*?Goal:\*\*?\s*([^*]+)(?=\*\*Week \d+:|Additional Resources|\Z)', content, re.DOTALL)
    
    print("\nFound Week Sections:")
    for week_match in week_matches:
        week_num = week_match.group(1)
        week_content = week_match.group(2).strip()
        print(f"\nWeek {week_num}:")
        print(f"Content preview: {week_content[:100]}...")

class SavePathView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            title = request.data.get("learningPathTitle")
            deadline=request.data.get("deadline")
            last_response = ChatHistory.objects.filter(
                user=request.user, 
                is_ai_response=True
            ).order_by('-created_at').first()
            
            if not last_response:
                return Response({
                    "isSuccess": False, 
                    "error": "No chat history to save"
                }, status=400)

            # Debug print
            print("\n=== Original Content ===")
            print(last_response.message[:500])
            print_content_sections(last_response.message)
            
            # Parse content
            tasks = parse_learning_path_content(last_response.message)
            
            print(f"\n=== Parsed {len(tasks)} Tasks ===")
            for task in tasks:
                print(f"\nCategory: {task['category']}")
                print(f"Title: {task['title']}")
                print(f"Week Number: {task.get('week_number')}")
                print(f"Description preview: {task['description'][:100]}...")

            # Create learning path
            learning_path = LearningPath.objects.create(
                student=request.user,
                title=title,
                deadline=deadline
            )

            # Create tasks
            created_tasks = []
            for task_data in tasks:
                task = Task.objects.create(
                    learning_path=learning_path,
                    title=task_data['title'],
                    description=task_data['description'],
                    category=task_data['category'],
                    week_number=task_data.get('week_number'),
                    order=task_data['order']
                )
                created_tasks.append(task)

            return Response({
                "isSuccess": True, 
                "message": f"Learning path created successfully with {len(created_tasks)} tasks",
                "taskCount": len(created_tasks)
            })
            
        except Exception as e:
            print(f"Error in SavePathView: {e}")
            import traceback
            traceback.print_exc()
            return Response({"isSuccess": False, "error": str(e)}, status=500)
class GetPathsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            paths = LearningPath.objects.filter(student=request.user)
            serializer = LearningPathsSerializer(paths, many=True)
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

    def delete(self, request, learning_path_id):
        try:
            path = get_object_or_404(LearningPath, id=learning_path_id, student=request.user)
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




class ToggleTaskCompletionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        task_id = request.data.get('taskId')
        task = get_object_or_404(Task, id=task_id)

        # Ensure the user owns the learning path
        if task.learning_path.student != request.user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        # Toggle the completion state
        task.is_completed = not task.is_completed
        task.save()

        return Response({
            'isSuccess': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'is_completed': task.is_completed,
            }
        }, status=status.HTTP_200_OK)
