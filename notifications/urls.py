from django.urls import path
from .views import inbox, mark_read

urlpatterns = [
    path("", inbox, name="notif_inbox"),
    path("read/<int:notif_id>/", mark_read, name="notif_read"),
]
