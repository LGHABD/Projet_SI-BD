from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def inbox(request):
    notifs = request.user.notifications.order_by("-date_envoi")
    return render(request, "notifications/inbox.html", {"notifs": notifs})

@login_required
def mark_read(request, notif_id: int):
    n = get_object_or_404(Notification, id=notif_id, user=request.user)
    n.is_read = True
    n.save(update_fields=["is_read"])
    return redirect("notif_inbox")
