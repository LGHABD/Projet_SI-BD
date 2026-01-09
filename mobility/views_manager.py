from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count

from accounts.decorators import role_required
from .services.selection import SelectionConfig, run_ranking, fifo_assign

from mobility.models import Student, SelectionResult, Affectation, Desiderata, DocumentAdministratif

@role_required("MOBILITY_MANAGER")
def run_selection(request):
    if request.method == "POST":
        annee = request.POST.get("annee_univ", "2024/2025")
        cfg = SelectionConfig(annee_univ=annee)
        n = run_ranking(cfg)
        messages.success(request, f"Classement terminé. {n} étudiants classés.")
        return redirect("manager_run_selection")
    return render(request, "mobility/manager/run_selection.html")

@role_required("MOBILITY_MANAGER")
def run_fifo(request):
    if request.method == "POST":
        annee = request.POST.get("annee_univ", "2024/2025")
        cfg = SelectionConfig(annee_univ=annee)
        stats = fifo_assign(cfg)
        messages.success(request, f"Affectation FIFO : {stats['assigned']} affectés, {stats['waiting']} en attente.")
        return redirect("manager_run_fifo")
    return render(request, "mobility/manager/fifo_assign.html")

@role_required("MOBILITY_MANAGER")
def stats(request):
    # mini dashboard
    kpi = {
        "students_total": Student.objects.count(),
        "students_eligible": Student.objects.filter(statut=Student.Status.ELIGIBLE).count(),
        "desiderata_submitted": Desiderata.objects.filter(statut=Desiderata.Status.SUBMITTED).count(),
        "assigned": Affectation.objects.count(),
        "docs_pending": DocumentAdministratif.objects.filter(statut_validation=DocumentAdministratif.Validation.PENDING).count(),
    }
    top_filiere = Student.objects.values("filiere__nom").annotate(n=Count("id")).order_by("-n")[:5]
    return render(request, "mobility/manager/stats.html", {"kpi": kpi, "top_filiere": top_filiere})
