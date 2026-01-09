from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages

from accounts.decorators import role_required
from .models import Student, Desiderata, DesiderataChoice, DocumentAdministratif, AlignmentPlace

@role_required("STUDENT")
def candidature(request):
    s: Student = request.user.student_profile
    return render(request, "mobility/student/candidature.html", {"student": s})

@role_required("STUDENT")
def desiderata(request):
    s: Student = request.user.student_profile
    des, _ = Desiderata.objects.get_or_create(student=s)

    if request.method == "POST":
        des.choices.all().delete()
        # place_rank_1=place_id, place_rank_2=place_id ...
        ranks = []
        for k, v in request.POST.items():
            if k.startswith("place_rank_") and v.strip():
                rank = int(k.replace("place_rank_", ""))
                ranks.append((rank, int(v)))

        ranks.sort(key=lambda x: x[0])
        for rank, place_id in ranks:
            DesiderataChoice.objects.create(desiderata=des, place_id=place_id, rank=rank)

        des.statut = Desiderata.Status.SUBMITTED
        des.date_soumission = timezone.now()
        des.save(update_fields=["statut", "date_soumission"])

        s.statut = Student.Status.DESIDERATA_SUBMITTED
        s.save(update_fields=["statut"])

        messages.success(request, "Desiderata soumis. Aucun changement n’est accepté après soumission.")
        return redirect("student_desiderata")

    places = AlignmentPlace.objects.filter(filiere_ensias=s.filiere).select_related("partenaire")
    return render(request, "mobility/student/desiderata.html", {"student": s, "desiderata": des, "places": places})

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
    return render(request, "mobility/student/documents.html", {"student": s, "docs": docs})

@role_required("STUDENT")
def results(request):
    s: Student = request.user.student_profile
    return render(request, "mobility/student/results.html", {"student": s})
