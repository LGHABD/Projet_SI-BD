from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="partner_dashboard"),
    path("decisions/", views.decisions, name="partner_decisions"),
    path("documents/", views.documents, name="partner_documents"),
    path("messages/", views.messages_inbox, name="partner_messages"),
]
