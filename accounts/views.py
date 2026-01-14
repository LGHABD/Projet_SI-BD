from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import LoginForm


class ENSIASLogoutView(LogoutView):
    """Déconnexion -> retour page de sélection de rôle."""
    next_page = reverse_lazy("role_select")


class ENSIASLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["selected_role"] = self.request.GET.get("role", "")
        return ctx
