from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=120, default="Notification")
    message = models.TextField()
    type_notif = models.CharField(max_length=50, default="INFO")
    date_envoi = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.type_notif}] {self.user} - {self.date_envoi:%Y-%m-%d}"
