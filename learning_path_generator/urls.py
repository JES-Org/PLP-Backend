from django.urls import path
from .views import(
    HealthCheckView,
    RestartSessionView,
    GreetView,
    DetailView,
    GeneratePathView,
    SavePathView,
    GetPathsView,
    GetPathView,
    DeletePathView,
    ChatHistoryView,
    MarkPathCompletedView,
    ToggleTaskCompletionView,
)
urlpatterns = [
    path('alive/', HealthCheckView.as_view(), name='health_check'),
    path('restart/', RestartSessionView.as_view(), name='restart_session'),
    path('greet/', GreetView.as_view(), name='greet'),
    path('detail/', DetailView.as_view(), name='detail'),
    path('generate/', GeneratePathView.as_view(), name='generate_path'),
    path('save/', SavePathView.as_view(), name='save_path'),
    path('all-paths/', GetPathsView.as_view(), name='get_paths'),
    path('<str:learning_path_id>/get/', GetPathView.as_view(), name='get_path'),
    path('<str:learning_path_id>/delete/', DeletePathView.as_view(), name='delete_path'),
    path('chat-history/', ChatHistoryView.as_view(), name='get-history'),
    path('mark-completed/<int:pk>/', MarkPathCompletedView.as_view(), name='mark_completed'),
    path('learning-path/toggle-task/', ToggleTaskCompletionView.as_view(), name='toggle-task'),


]