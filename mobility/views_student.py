from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q

from accounts.decorators import role_required
from core.models import Phase
from partners.models import PartnerDecision
from .models import Student, Desiderata, DesiderataChoice, DocumentAdministratif, AlignmentPlace

@role_required("STUDENT")
def candidature(request):
    s: Student = request.user.student_profile
    current_phase = Phase.objects.filter(statut=Phase.Status.ACTIVE).order_by("ordre").first()
    return render(
        request,
        "mobility/student/candidature.html",
        {"student": s, "active_nav": "candidature", "current_phase": current_phase},
    )

@role_required("STUDENT")
def desiderata(request):
    s: Student = request.user.student_profile
    des, _ = Desiderata.objects.get_or_create(student=s)

    active_phase = Phase.objects.filter(statut=Phase.Status.ACTIVE).order_by("ordre").first()
    phase_open = bool(active_phase and "Desiderata" in active_phase.nom)

    if request.method == "POST":
        if not phase_open:
            messages.error(request, "La phase Desiderata est fermee.")
            return redirect("student_desiderata")

        des.choices.all().delete()
        # place_rank_1=place_id, place_rank_2=place_id ...
        ranks = []
        for k, v in request.POST.items():
            if k.startswith("place_rank_") and v.strip():
                rank = int(k.replace("place_rank_", ""))
                ranks.append((rank, int(v)))

        ranks.sort(key=lambda x: x[0])
        if len(ranks) < 3:
            messages.error(request, "Veuillez choisir au moins 3 etablissements.")
            return redirect("student_desiderata")
        for rank, place_id in ranks:
            DesiderataChoice.objects.create(desiderata=des, place_id=place_id, rank=rank)

        des.statut = Desiderata.Status.SUBMITTED
        des.date_soumission = timezone.now()
        des.save(update_fields=["statut", "date_soumission"])

        s.statut = Student.Status.DESIDERATA_SUBMITTED
        s.save(update_fields=["statut"])

        messages.success(request, "Desiderata soumis. Aucun changement n’est accepté après soumission.")
        return redirect("student_desiderata")

    places = AlignmentPlace.objects.filter(
        Q(filiere_ensias=s.filiere) | Q(open_to_all=True)
    ).select_related("partenaire")
    return render(
        request,
        "mobility/student/desiderata.html",
        {"student": s, "desiderata": des, "places": places, "phase_open": phase_open, "active_nav": "desiderata"},
    )

@role_required("STUDENT")
def documents(request):
    s: Student = request.user.student_profile
    if request.method == "POST":
        doc_type = request.POST.get("type_doc")
        fichier = request.FILES.get("fichier")
        if fichier and doc_type:
            DocumentAdministratif.objects.create(student=s, type_doc=doc_type, fichier=fichier)
            messages.success(request, "Document téléversé.")
            return redirect("student_documents")
        messages.error(request, "Veuillez choisir un type et un fichier.")

    docs = s.documents.order_by("-date_upload")
    required_types = ["CV", "LETTRE_MOTIV", "RELEVES", "CONVENTION"]
    uploaded = set(docs.values_list("type_doc", flat=True))
    done = sum(1 for t in required_types if t in uploaded)
    progress = int((done / len(required_types)) * 100) if required_types else 0
    return render(
        request,
        "mobility/student/documents.html",
        {"student": s, "docs": docs, "active_nav": "documents", "progress": progress, "docs_done": done, "docs_required": len(required_types)},
    )

@role_required("STUDENT")
def results(request):
    s: Student = request.user.student_profile
    partner_decision = None
    if hasattr(s, "affectation"):
        partner_decision = PartnerDecision.objects.filter(student=s).first()
    return render(
        request,
        "mobility/student/results.html",
        {"student": s, "active_nav": "results", "partner_decision": partner_decision},
    )
