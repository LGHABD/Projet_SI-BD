import csv
from django.core.management.base import BaseCommand
from mobility.models import Student

class Command(BaseCommand):
    help = "Export students CSV: cne,apogee,filiere,statut,email"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **opts):
        path = opts["csv_path"]
        qs = Student.objects.select_related("user","filiere").all()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["cne","code_apogee","filiere","statut","email"])
            for s in qs:
                writer.writerow([s.cne, s.code_apogee, s.filiere.nom, s.statut, s.user.email])
        self.stdout.write(self.style.SUCCESS(f"Export OK: {qs.count()} étudiants -> {path}"))
