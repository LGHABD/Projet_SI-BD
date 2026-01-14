from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from accounts.decorators import role_required
from mobility.models import Affectation, DocumentAdministratif
from .models import PartnerDecision


def _get_partner(user):
    return getattr(user, "partenaire", None)


@role_required("PARTNER")
def dashboard(request):
    partner = _get_partner(request.user)
    affectations = Affectation.objects.select_related("place", "place__partenaire", "student", "student__user")
    if partner:
        affectations = affectations.filter(place__partenaire=partner)
    else:
        affectations = affectations.none()

    kpi = {
        "assigned": affectations.count(),
        "accepted": PartnerDecision.objects.filter(partenaire=partner, resultat="ACCEPTED").count() if partner else 0,
        "refused": PartnerDecision.objects.filter(partenaire=partner, resultat="REFUSED").count() if partner else 0,
    }
    return render(
        request,
        "partners/dashboard.html",
        {"affectations": affectations, "kpi": kpi, "active_nav": "dashboard"},
    )


@role_required("PARTNER")
def decisions(request):
    partner = _get_partner(request.user)
    affectations = Affectation.objects.select_related("place", "place__partenaire", "student", "student__user")
    if partner:
        affectations = affectations.filter(place__partenaire=partner)
    else:
        affectations = affectations.none()

    if request.method == "POST":
        affectation_id = request.POST.get("affectation_id")
        decision = request.POST.get("decision")
        lettre = request.FILES.get("lettre_reponse")
        aff = get_object_or_404(Affectation, id=affectation_id)
        pd = PartnerDecision.objects.filter(
            partenaire=aff.place.partenaire, student=aff.student, affectation=aff
        ).first()
        if not pd and not decision:
            messages.error(request, "Veuillez choisir une decision.")
            return redirect("partner_decisions")
        if not pd:
            pd = PartnerDecision.objects.create(
                partenaire=aff.place.partenaire,
                student=aff.student,
                affectation=aff,
                resultat=decision,
            )
        if decision in ["ACCEPTED", "REFUSED"]:
            pd.resultat = decision
            pd.decision_partenaire = decision
            aff.student.statut = "ACCEPTED" if decision == "ACCEPTED" else "REFUSED"
            aff.student.save(update_fields=["statut"])
        if lettre:
            pd.lettre_reponse = lettre
        pd.save()
        aff.decision_partenaire = decision or aff.decision_partenaire
        if lettre:
            aff.lettre_reponse = lettre
        aff.save(update_fields=["decision_partenaire", "lettre_reponse"])
        messages.success(request, "Decision enregistree.")
        return redirect("partner_decisions")

    existing = {
        d.student_id: d for d in PartnerDecision.objects.filter(partenaire=partner)
    } if partner else {}
    rows = []
    for a in affectations:
        rows.append({"affectation": a, "decision": existing.get(a.student_id)})
    return render(
        request,
        "partners/decisions.html",
        {"rows": rows, "active_nav": "decisions"},
    )


@role_required("PARTNER")
def documents(request):
    partner = _get_partner(request.user)
    docs = DocumentAdministratif.objects.select_related("student", "student__user")
    if partner:
        docs = docs.filter(student__affectation__place__partenaire=partner)
    else:
        docs = docs.none()
    return render(request, "partners/documents.html", {"docs": docs, "active_nav": "documents"})


@role_required("PARTNER")
def messages_inbox(request):
    notifs = request.user.notifications.order_by("-date_envoi")
    return render(request, "partners/messages.html", {"notifs": notifs, "active_nav": "messages"})
