import csv
from django.core.management.base import BaseCommand
from mobility.models import Student, StudentNote
from core.models import Module

class Command(BaseCommand):
    help = "Import notes CSV: cne,module_code,annee_univ,note"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **opts):
        path = opts["csv_path"]
        created = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                student = Student.objects.get(cne=row["cne"])
                module = Module.objects.get(code=row["module_code"])
                note = float(row["note"])
                annee = row["annee_univ"]
                StudentNote.objects.update_or_create(
                    student=student, module=module, annee_univ=annee,
                    defaults={"note": note}
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Import OK: {created} lignes"))
