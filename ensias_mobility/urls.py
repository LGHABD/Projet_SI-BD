from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import ENSIASLoginView, ENSIASLogoutView
from dashboard.views import home,role_select

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", role_select, name="role_select"),  # page d’orientation
    path("home/", home, name="home"),           # dashboard selon rôle
    path("login/", ENSIASLoginView.as_view(), name="login"),
    path("logout/", ENSIASLogoutView.as_view(), name="logout"),

    path("mobility/", include("mobility.urls")),
    path("partners/", include("partners.urls")),
    path("notifications/", include("notifications.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
