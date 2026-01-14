from django.core.mail import send_mail
from django.conf import settings
from .models import Notification


def notify_user(user, title: str, body: str = "", send_email: bool = False, type_notif: str = "INFO"):
    """
    Notify a user in-app and optionally by email.
    Backward compatible: if body is empty, title is used as message text.
    """
    message = body or title
    Notification.objects.create(
        user=user,
        title=title or "Notification",
        message=message,
        type_notif=type_notif,
    )
    if send_email and getattr(user, "email", None):
        send_mail(
            subject=f"[ENSIAS Mobilite] {title or 'Notification'}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
