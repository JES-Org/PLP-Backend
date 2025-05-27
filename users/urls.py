from django.urls import path

from .views import( CustomTokenObtainPairView, GetStudentByIdView, GetStudentByUserIdView, GetTeacherByIdView, 
                   GetTeacherByUserIdView, RegisterView, UpdateStudentProfileView, 
                   UpdateTeacherProfileView, send_otp, verify_otp,ResetPasswordView,DeleteAccountView,
                   )
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path("otp/send/", send_otp, name="send-otp"),
    path("otp/verify/", verify_otp, name="verify-otp"),
    path("teacher/<str:user_id>/", GetTeacherByUserIdView.as_view(), name="get-teacher-by-user-id"),
    path("student/<str:user_id>/", GetStudentByUserIdView.as_view(), name="get-student-by-user-id"),
    path('student-id/<str:student_id>/', GetStudentByIdView.as_view(), name='get-student-by-id'),
    path('teacher-id/<str:teacher_id>/', GetTeacherByIdView.as_view(), name='get-teacher-by-id'),
    path('student/profile/update/', UpdateStudentProfileView.as_view(), name='update-student-profile'),
    path('teacher/profile/update/', UpdateTeacherProfileView.as_view(), name='update-teacher-profile'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
]