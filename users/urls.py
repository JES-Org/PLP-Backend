from django.urls import path

from .views import CustomTokenObtainPairView, RegisterView, send_otp, verify_otp

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("otp/send/", send_otp, name="send-otp"),
    path("otp/verify/", verify_otp, name="verify-otp"),
]

