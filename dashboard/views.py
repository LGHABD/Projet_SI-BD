from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from core.models import Phase
from mobility.models import Desiderata, DocumentAdministratif, Student

def role_select(request):
    # Si l’utilisateur est déjà connecté, on l’envoie au dashboard
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "dashboard/role_select.html")


@login_required
def home(request):
    r = request.user.role
    if r == "STUDENT":
        s: Student = request.user.student_profile

        phases = list(Phase.objects.order_by("ordre"))
        current_phase = (
            Phase.objects.filter(statut=Phase.Status.ACTIVE).order_by("ordre").first()
            or (phases[0] if phases else None)
        )

        # KPI: desiderata (nb de choix)
        try:
            des = s.desiderata
            nb_desiderata = des.choices.count()
        except Desiderata.DoesNotExist:
            nb_desiderata = 0

        # KPI: documents
        required_types = ["CV", "LETTRE_MOTIV", "RELEVES", "CONVENTION"]
        uploaded = set(
            DocumentAdministratif.objects.filter(student=s)
            .values_list("type_doc", flat=True)
            .distinct()
        )
        docs_done = sum(1 for t in required_types if t in uploaded)

        # Statut global (candidature)
        candidature_status = s.get_statut_display() if hasattr(s, "get_statut_display") else s.statut

        ctx = {
            "phases": phases,
            "current_phase": current_phase,
            "nb_desiderata": nb_desiderata,
            "docs_done": docs_done,
            "docs_required": len(required_types),
            "candidature_status": candidature_status,
            "active_nav": "dashboard",
        }

        return render(request, "student/dashboard.html", ctx)
    if r == "MOBILITY_MANAGER":
        return redirect("manager_stats")
    if r == "SCHOOL_ADMIN":
        return redirect("school_admin_dashboard")
    if r == "DIRECTOR":
        return redirect("director_dashboard")
    if r == "PARTNER":
        return redirect("partner_dashboard")
    return render(request, "dashboard/role_select.html")


@login_required
def student_messages(request):
    """Vue 'Messages' simple (s'appuie sur les notifications)."""
    if request.user.role != "STUDENT":
        return redirect("home")
    notifs = request.user.notifications.order_by("-date_envoi")
    return render(request, "student/messages.html", {"notifs": notifs, "active_nav": "messages"})


@login_required
def student_chatbot(request):
    if request.user.role != "STUDENT":
        return redirect("home")
    return render(request, "student/chatbot.html", {"active_nav": "chatbot"})


@require_POST
@login_required
def student_chatbot_api(request):
    """Mini-chatbot local (règles), sans API externe."""
    if request.user.role != "STUDENT":
        return JsonResponse({"error": "forbidden"}, status=403)

    msg = ""
    if request.content_type and request.content_type.startswith("application/json"):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            payload = {}
        msg = (payload.get("message") or "").strip().lower()
    else:
        msg = (request.POST.get("message") or "").strip().lower()
    if not msg:
        return JsonResponse({"reply": "Ecris une question pour que je puisse t'aider."})

    # Réponses simples basées sur mots-clés
    if "phase" in msg or "avancement" in msg:
        active = Phase.objects.filter(statut="ACTIVE").order_by("ordre").first()
        if active:
            ans = f"La phase actuelle est {active.nom}. Debut: {active.date_debut or '-'}, fin: {active.date_fin or '-'}."
        else:
            ans = "Aucune phase n'est marquée ACTIVE pour le moment."
        return JsonResponse({"reply": ans})

    if "document" in msg or "cv" in msg or "lettre" in msg:
        return JsonResponse({
            "reply": "Tu peux deposer tes documents dans Mes documents. Documents typiques: CV, Lettre de motivation, Releves, Convention."
        })

    if "desiderata" in msg or "école" in msg or "ecole" in msg:
        return JsonResponse({
            "reply": "Dans Mes desiderata, ajoute tes ecoles puis classe-les (1, 2, 3...)."
        })

    if "resultat" in msg or "résultat" in msg:
        return JsonResponse({
            "reply": "Les resultats apparaitront dans Resultats des qu'ils seront publies. Tu recevras aussi une notification."
        })

    return JsonResponse({
        "reply": "Je peux t'aider sur: phases, documents, desiderata, resultats. Exemple: 'Quelle est la phase actuelle ?'"
    })


@login_required
def student_calendar(request):
    if request.user.role != "STUDENT":
        return redirect("home")
    return render(request, "student/calendar.html", {"active_nav": "calendar"})


@login_required
def student_comparison(request):
    if request.user.role != "STUDENT":
        return redirect("home")
    return render(request, "student/comparison.html", {"active_nav": "comparison"})


# Compat: dashboard/urls.py utilise chatbot_api
chatbot_api = student_chatbot_api
