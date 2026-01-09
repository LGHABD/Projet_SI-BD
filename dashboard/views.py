from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def role_select(request):
    # Si déjà connecté → aller vers le dashboard (home)
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "dashboard/role_select.html")


@login_required
def home(request):
    role = getattr(request.user, "role", "")

    role_templates = {
        "STUDENT": "dashboard/student_home.html",
        "MOBILITY_MANAGER": "dashboard/manager_home.html",
        "SCHOOL_ADMIN": "dashboard/admin_home.html",
        "DIRECTOR": "dashboard/director_home.html",
    }

    # Partenaire -> page dédiée
    if role == "PARTNER":
        return redirect("partner_decisions")

    # Rôles avec templates directs
    template = role_templates.get(role)
    if template:
        return render(request, template)

    # Si rôle inconnu -> revenir à role_select
    return redirect("role_select")
