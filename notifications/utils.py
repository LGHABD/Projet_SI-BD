from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

def notify_user(user, message: str, type_notif: str = "INFO", send_email_flag: bool = True):
    Notification.objects.create(user=user, message=message, type_notif=type_notif)
    if send_email_flag and getattr(user, "email", None):
        send_mail(
            subject="[ENSIAS Mobilité] Notification",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
