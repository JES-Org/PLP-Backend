from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(user_email: str, otp: str, user_name: str = None):
    subject = 'Your One-Time Password (OTP)'
    user_display_name = user_name or 'User'
    app_name = getattr(settings, 'APP_NAME', 'Our Service')

    message = (
        f"Hello {user_display_name},\n\n"
        f"Your One-Time Password is: {otp}\n\n"
        f"This OTP is valid for a limited time. Please do not share it with anyone.\n\n"
        f"If you did not request this OTP, please ignore this email.\n\n"
        f"Thanks,\nThe {app_name} Team"
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        print(f"OTP email sent successfully to {user_email} (OTP: {otp})")
        return True
    except Exception as e:
        print(f"Error sending OTP email to {user_email}: {e}")
        return False
