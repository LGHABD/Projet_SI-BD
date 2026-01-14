import csv
from io import StringIO
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import User
from core.models import Phase, Filiere, Module
from mobility.models import Student, StudentNote, DocumentAdministratif, Affectation

DEFAULT_PASS = "Pass12345!"


@role_required("SCHOOL_ADMIN")
def dashboard(request):
    phases = Phase.objects.order_by("ordre")
    status_counts = Student.objects.values("statut").annotate(n=Count("id")).order_by("-n")
    return render(
        request,
        "admin/dashboard.html",
        {"phases": phases, "status_counts": status_counts, "active_nav": "dashboard"},
    )


@role_required("SCHOOL_ADMIN")
def import_csv(request):
    preview = []
    logs = []
    created = 0
    import_type = "students"

    if request.method == "POST" and request.FILES.get("csv_file"):
        import_type = request.POST.get("import_type", "students")
        file_obj = request.FILES["csv_file"]
        decoded = file_obj.read().decode("utf-8", errors="ignore")
        reader = csv.DictReader(StringIO(decoded))
        rows = list(reader)
        preview = rows[:8]

        if import_type == "students":
            required = {"email", "cne", "code_apogee", "filiere", "first_name", "last_name"}
            if not required.issubset(reader.fieldnames or []):
                messages.error(request, "Colonnes requises manquantes: email,cne,code_apogee,filiere,first_name,last_name")
            else:
                for row in rows:
                    try:
                        filiere, _ = Filiere.objects.get_or_create(nom=row["filiere"].strip())
                        user, created_user = User.objects.get_or_create(
                            username=row["email"].strip(),
                            defaults={
                                "email": row["email"].strip(),
                                "first_name": row["first_name"].strip(),
                                "last_name": row["last_name"].strip(),
                                "role": "STUDENT",
                            },
                        )
                        if created_user:
                            user.set_password(DEFAULT_PASS)
                            user.save()
                        Student.objects.get_or_create(
                            user=user,
                            defaults={
                                "cne": row["cne"].strip(),
                                "code_apogee": row["code_apogee"].strip(),
                                "telephone": row.get("telephone", "").strip(),
                                "filiere": filiere,
                            },
                        )
                        created += 1
                    except Exception as exc:
                        logs.append(f"Ligne ignoree: {row} ({exc})")
                messages.success(request, f"Import etudiants termine: {created} lignes.")

        elif import_type == "notes":
            required = {"cne", "module_code", "annee_univ", "note"}
            if not required.issubset(reader.fieldnames or []):
                messages.error(request, "Colonnes requises manquantes: cne,module_code,annee_univ,note")
            else:
                for row in rows:
                    try:
                        student = Student.objects.get(cne=row["cne"].strip())
                        module_code = row["module_code"].strip()
                        module = Module.objects.filter(code=module_code).first()
                        if not module:
                            name = row.get("module_name", module_code)
                            sem = row.get("semestre", "S1")
                            typ = row.get("type_module", "commun")
                            module = Module.objects.create(code=module_code, nom=name, semestre=sem, type_module=typ)
                        StudentNote.objects.update_or_create(
                            student=student,
                            module=module,
                            annee_univ=row["annee_univ"].strip(),
                            defaults={"note": float(row["note"])},
                        )
                        created += 1
                    except Exception as exc:
                        logs.append(f"Ligne ignoree: {row} ({exc})")
                messages.success(request, f"Import notes termine: {created} lignes.")
        else:
            messages.error(request, "Type d'import invalide.")

    return render(
        request,
        "admin/import_csv.html",
        {"preview": preview, "logs": logs, "active_nav": "import", "import_type": import_type},
    )


@role_required("SCHOOL_ADMIN")
def export_csv(request):
    if request.method == "POST":
        status = request.POST.get("statut", "")
        filiere = request.POST.get("filiere", "")
        partner = request.POST.get("partner", "")

        qs = Student.objects.select_related("user", "filiere")
        if status:
            qs = qs.filter(statut=status)
        if filiere:
            qs = qs.filter(filiere__id=filiere)
        if partner:
            qs = qs.filter(affectation__place__partenaire__id=partner)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=students_export.csv"
        writer = csv.writer(response)
        writer.writerow(["cne", "code_apogee", "nom", "email", "filiere", "statut"])
        for s in qs:
            writer.writerow([s.cne, s.code_apogee, s.user.get_full_name(), s.user.email, s.filiere.nom, s.statut])
        return response

    filieres = Filiere.objects.order_by("nom")
    partners = Affectation.objects.values("place__partenaire__id", "place__partenaire__nom").distinct()
    return render(
        request,
        "admin/export_csv.html",
        {"filieres": filieres, "partners": partners, "active_nav": "export"},
    )


@role_required("SCHOOL_ADMIN")
def documents(request):
    docs = DocumentAdministratif.objects.select_related("student", "student__user").order_by("-date_upload")
    if request.method == "POST":
        doc_id = request.POST.get("doc_id")
        status = request.POST.get("status")
        doc = DocumentAdministratif.objects.get(pk=doc_id)
        if status in [DocumentAdministratif.Validation.VALID, DocumentAdministratif.Validation.INVALID]:
            doc.statut_validation = status
            doc.validated_by = request.user
            doc.validated_at = timezone.now()
            doc.save(update_fields=["statut_validation", "validated_by", "validated_at"])
            messages.success(request, "Document mis a jour.")
        return redirect("school_admin_documents")
    return render(
        request,
        "admin/documents.html",
        {"docs": docs, "active_nav": "documents"},
    )
