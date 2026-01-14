from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth import get_user_model

from accounts.decorators import role_required
from core.models import Partenaire, Phase
from mobility.models import (
    Student,
    SelectionResult,
    Affectation,
    Desiderata,
    DocumentAdministratif,
    AlignmentPlace,
    Entretien,
)
from mobility.services.selection import SelectionConfig, run_ranking, fifo_assign
from notifications.utils import notify_user

from .forms import (
    PartnerForm,
    PhaseForm,
    AlignmentPlaceForm,
    InterviewForm,
    NotificationForm,
)


@role_required("MOBILITY_MANAGER")
def stats(request):
    kpi = {
        "students_total": Student.objects.count(),
        "students_eligible": Student.objects.filter(statut=Student.Status.ELIGIBLE).count(),
        "selected": SelectionResult.objects.count(),
        "assigned": Affectation.objects.count(),
        "docs_ok": DocumentAdministratif.objects.filter(
            statut_validation=DocumentAdministratif.Validation.VALID
        ).count(),
    }
    by_filiere = Student.objects.values("filiere__nom").annotate(n=Count("id")).order_by("-n")[:6]
    by_partner = Affectation.objects.values("place__partenaire__nom").annotate(n=Count("id")).order_by("-n")[:6]
    return render(
        request,
        "mobility/manager/stats.html",
        {"kpi": kpi, "by_filiere": by_filiere, "by_partner": by_partner, "active_nav": "dashboard"},
    )


@role_required("MOBILITY_MANAGER")
def run_selection(request):
    if request.method == "POST":
        annee = request.POST.get("annee_univ", "2024/2025")
        cfg = SelectionConfig(annee_univ=annee)
        n = run_ranking(cfg)
        messages.success(request, f"Classement termine. {n} etudiants classes.")
        return redirect("manager_run_selection")
    return render(request, "mobility/manager/run_selection.html", {"active_nav": "selection"})


@role_required("MOBILITY_MANAGER")
def run_fifo(request):
    if request.method == "POST":
        annee = request.POST.get("annee_univ", "2024/2025")
        cfg = SelectionConfig(annee_univ=annee)
        stats = fifo_assign(cfg)
        messages.success(request, f"Affectation FIFO : {stats['assigned']} affectes, {stats['waiting']} en attente.")
        return redirect("manager_run_fifo")
    return render(request, "mobility/manager/fifo_assign.html", {"active_nav": "assign"})


@role_required("MOBILITY_MANAGER")
def partners_list(request):
    partners = Partenaire.objects.order_by("nom")
    form = PartnerForm()
    if request.method == "POST":
        form = PartnerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Partenaire ajoute.")
            return redirect("manager_partners")
    return render(
        request,
        "mobility/manager/partners_list.html",
        {"partners": partners, "form": form, "active_nav": "partners"},
    )


@role_required("MOBILITY_MANAGER")
def partners_edit(request, pk):
    partner = get_object_or_404(Partenaire, pk=pk)
    form = PartnerForm(instance=partner)
    if request.method == "POST":
        form = PartnerForm(request.POST, instance=partner)
        if form.is_valid():
            form.save()
            messages.success(request, "Partenaire mis a jour.")
            return redirect("manager_partners")
    return render(request, "mobility/manager/partners_edit.html", {"form": form, "partner": partner, "active_nav": "partners"})


@role_required("MOBILITY_MANAGER")
def partners_delete(request, pk):
    partner = get_object_or_404(Partenaire, pk=pk)
    if request.method == "POST":
        partner.delete()
        messages.success(request, "Partenaire supprime.")
        return redirect("manager_partners")
    return render(request, "mobility/manager/partners_delete.html", {"partner": partner, "active_nav": "partners"})


@role_required("MOBILITY_MANAGER")
def places_list(request):
    places = AlignmentPlace.objects.select_related("partenaire", "filiere_ensias").order_by("-annee", "partenaire__nom")
    form = AlignmentPlaceForm()
    if request.method == "POST":
        form = AlignmentPlaceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Place ajoutee.")
            return redirect("manager_places")
    return render(
        request,
        "mobility/manager/places_list.html",
        {"places": places, "form": form, "active_nav": "places"},
    )


@role_required("MOBILITY_MANAGER")
def places_edit(request, pk):
    place = get_object_or_404(AlignmentPlace, pk=pk)
    form = AlignmentPlaceForm(instance=place)
    if request.method == "POST":
        form = AlignmentPlaceForm(request.POST, instance=place)
        if form.is_valid():
            form.save()
            messages.success(request, "Place mise a jour.")
            return redirect("manager_places")
    return render(request, "mobility/manager/places_edit.html", {"form": form, "place": place, "active_nav": "places"})


@role_required("MOBILITY_MANAGER")
def places_delete(request, pk):
    place = get_object_or_404(AlignmentPlace, pk=pk)
    if request.method == "POST":
        place.delete()
        messages.success(request, "Place supprimee.")
        return redirect("manager_places")
    return render(request, "mobility/manager/places_delete.html", {"place": place, "active_nav": "places"})


@role_required("MOBILITY_MANAGER")
def phases_list(request):
    phases = Phase.objects.order_by("ordre")
    form = PhaseForm()
    if request.method == "POST":
        form = PhaseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Phase ajoutee.")
            return redirect("manager_phases")
    return render(
        request,
        "mobility/manager/phases_list.html",
        {"phases": phases, "form": form, "active_nav": "phases"},
    )


@role_required("MOBILITY_MANAGER")
def phases_edit(request, pk):
    phase = get_object_or_404(Phase, pk=pk)
    form = PhaseForm(instance=phase)
    if request.method == "POST":
        form = PhaseForm(request.POST, instance=phase)
        if form.is_valid():
            form.save()
            messages.success(request, "Phase mise a jour.")
            return redirect("manager_phases")
    return render(request, "mobility/manager/phases_edit.html", {"form": form, "phase": phase, "active_nav": "phases"})


@role_required("MOBILITY_MANAGER")
def phases_activate(request, pk):
    phase = get_object_or_404(Phase, pk=pk)
    if request.method == "POST":
        Phase.objects.filter(statut=Phase.Status.ACTIVE).update(statut=Phase.Status.CLOSED)
        phase.statut = Phase.Status.ACTIVE
        phase.save(update_fields=["statut"])
        messages.success(request, "Phase activee.")
        return redirect("manager_phases")
    return render(request, "mobility/manager/phases_activate.html", {"phase": phase, "active_nav": "phases"})


@role_required("MOBILITY_MANAGER")
def desiderata_validation(request):
    desideratas = Desiderata.objects.select_related(
        "student", "student__user", "student__filiere"
    ).prefetch_related("choices__place__partenaire")
    if request.method == "POST":
        des_id = request.POST.get("desiderata_id")
        action = request.POST.get("action")
        des = get_object_or_404(Desiderata, pk=des_id)
        if action in [Desiderata.Status.VALID, Desiderata.Status.INVALID, Desiderata.Status.RECTIFICATION]:
            des.statut = action
            des.validated_by = request.user
            des.validated_at = timezone.now()
            des.save(update_fields=["statut", "validated_by", "validated_at"])
            messages.success(request, "Statut du desiderata mis a jour.")
        return redirect("manager_desiderata_validation")
    return render(
        request,
        "mobility/manager/desiderata_validation.html",
        {"desideratas": desideratas, "active_nav": "desiderata"},
    )


@role_required("MOBILITY_MANAGER")
def interviews(request):
    students = Student.objects.select_related("user", "filiere").order_by("user__last_name")
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        student = get_object_or_404(Student, pk=student_id)
        try:
            existing = student.entretien
        except Entretien.DoesNotExist:
            existing = None
        form = InterviewForm(request.POST, instance=existing)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.student = student
            interview.save()
            messages.success(request, "Entretien mis a jour.")
            return redirect("manager_interviews")
    return render(
        request,
        "mobility/manager/interviews.html",
        {
            "students": students,
            "active_nav": "interviews",
            "interview_choices": Entretien.Decision.choices,
        },
    )


@role_required("MOBILITY_MANAGER")
def documents(request):
    docs = DocumentAdministratif.objects.select_related("student", "student__user").order_by("-date_upload")
    if request.method == "POST":
        doc_id = request.POST.get("doc_id")
        status = request.POST.get("status")
        doc = get_object_or_404(DocumentAdministratif, pk=doc_id)
        if status in [DocumentAdministratif.Validation.VALID, DocumentAdministratif.Validation.INVALID]:
            doc.statut_validation = status
            doc.validated_by = request.user
            doc.validated_at = timezone.now()
            doc.save(update_fields=["statut_validation", "validated_by", "validated_at"])
            messages.success(request, "Document mis a jour.")
        return redirect("manager_documents")
    return render(request, "mobility/manager/documents.html", {"docs": docs, "active_nav": "documents"})


@role_required("MOBILITY_MANAGER")
def notifications(request):
    form = NotificationForm()
    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["recipient_role"]
            title = form.cleaned_data["title"]
            body = form.cleaned_data["body"]
            send_email = form.cleaned_data["send_email"]

            if role == "STUDENT":
                users = [s.user for s in Student.objects.select_related("user")]
            elif role == "PARTNER":
                User = get_user_model()
                users = list(User.objects.filter(role="PARTNER").select_related("partenaire"))
            else:
                users = []

            for u in users:
                notify_user(u, title, body, send_email=send_email)

            messages.success(request, f"Notification envoyee a {len(users)} utilisateurs.")
            return redirect("manager_notifications")
    return render(request, "mobility/manager/notifications.html", {"form": form, "active_nav": "notifications"})
