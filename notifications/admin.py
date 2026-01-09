from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "type_notif", "date_envoi", "is_read")
    list_filter = ("type_notif", "is_read")
    search_fields = ("user__username", "user__email", "message")
