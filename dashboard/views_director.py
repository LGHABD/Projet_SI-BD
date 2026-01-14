import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Count

from accounts.decorators import role_required
from core.models import Filiere
from mobility.models import Student, Affectation


@role_required("DIRECTOR")
def dashboard(request):
    kpi = {
        "students": Student.objects.count(),
        "eligible": Student.objects.filter(statut=Student.Status.ELIGIBLE).count(),
        "assigned": Student.objects.filter(statut=Student.Status.ASSIGNED).count(),
        "accepted": Student.objects.filter(statut=Student.Status.ACCEPTED).count(),
    }
    by_filiere = Student.objects.values("filiere__nom").annotate(n=Count("id")).order_by("-n")[:6]
    by_partner = Affectation.objects.values("place__partenaire__nom").annotate(n=Count("id")).order_by("-n")[:6]
    return render(
        request,
        "director/dashboard.html",
        {"kpi": kpi, "by_filiere": by_filiere, "by_partner": by_partner, "active_nav": "dashboard"},
    )


@role_required("DIRECTOR")
def students_list(request):
    qs = Student.objects.select_related("user", "filiere")
    statut = request.GET.get("statut", "")
    filiere = request.GET.get("filiere", "")
    partner = request.GET.get("partner", "")

    if statut:
        qs = qs.filter(statut=statut)
    if filiere:
        qs = qs.filter(filiere__id=filiere)
    if partner:
        qs = qs.filter(affectation__place__partenaire__id=partner)

    filieres = Filiere.objects.order_by("nom")
    partners = Affectation.objects.values("place__partenaire__id", "place__partenaire__nom").distinct()
    return render(
        request,
        "director/students.html",
        {
            "students": qs,
            "filieres": filieres,
            "partners": partners,
            "active_nav": "students",
            "filters": {"statut": statut, "filiere": filiere, "partner": partner},
        },
    )


@role_required("DIRECTOR")
def export_csv(request):
    if request.method == "POST":
        statut = request.POST.get("statut", "")
        filiere = request.POST.get("filiere", "")
        partner = request.POST.get("partner", "")

        qs = Student.objects.select_related("user", "filiere")
        if statut:
            qs = qs.filter(statut=statut)
        if filiere:
            qs = qs.filter(filiere__id=filiere)
        if partner:
            qs = qs.filter(affectation__place__partenaire__id=partner)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=director_export.csv"
        writer = csv.writer(response)
        writer.writerow(["cne", "code_apogee", "nom", "email", "filiere", "statut"])
        for s in qs:
            writer.writerow([s.cne, s.code_apogee, s.user.get_full_name(), s.user.email, s.filiere.nom, s.statut])
        return response

    filieres = Filiere.objects.order_by("nom")
    partners = Affectation.objects.values("place__partenaire__id", "place__partenaire__nom").distinct()
    return render(
        request,
        "director/export.html",
        {"filieres": filieres, "partners": partners, "active_nav": "export"},
    )
