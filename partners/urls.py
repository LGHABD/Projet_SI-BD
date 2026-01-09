from django.urls import path
from .views import decisions

urlpatterns = [
    path("decisions/", decisions, name="partner_decisions"),
]
