from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from core.models import Filiere, Partenaire, Module, Phase
from mobility.models import Student, AlignmentPlace, StudentNote, Desiderata, DesiderataChoice
import random

PASS = "Pass12345!"

class Command(BaseCommand):
    help = "Créer des données de démo (comptes + référentiels + notes + places)"

    def handle(self, *args, **opts):
        # rôles
        manager = self._user("manager@ensias.ma", "Manager", "Mob", "MOBILITY_MANAGER")
        school_admin = self._user("admin@ensias.ma", "Admin", "Scolarite", "SCHOOL_ADMIN")
        director = self._user("director@ensias.ma", "Director", "ENSIAS", "DIRECTOR")
        partner_user = self._user("partner@partner.com", "Partner", "User", "PARTNER")

        # filières
        gl, _ = Filiere.objects.get_or_create(nom="GL", defaults={"pool":"POOL_GL"})
        iad, _ = Filiere.objects.get_or_create(nom="IAD", defaults={"pool":"POOL_IAD"})
        rc, _ = Filiere.objects.get_or_create(nom="RC", defaults={"pool":"POOL_RC"})

        # partenaires
        p1, _ = Partenaire.objects.get_or_create(nom="Université A", defaults={"pays":"France","email":"contact@unia.fr"})
        p2, _ = Partenaire.objects.get_or_create(nom="Université B", defaults={"pays":"Canada","email":"contact@unib.ca"})

        # phases
        today = timezone.now().date()
        Phase.objects.get_or_create(nom="Authentification", defaults={"date_debut":today, "ordre":1, "statut":"ACTIVE"})
        Phase.objects.get_or_create(nom="Sélection", defaults={"date_debut":today, "ordre":2, "statut":"NOT_STARTED"})
        Phase.objects.get_or_create(nom="Desiderata", defaults={"date_debut":today, "ordre":3, "statut":"NOT_STARTED"})
        Phase.objects.get_or_create(nom="Affectation FIFO", defaults={"date_debut":today, "ordre":4, "statut":"NOT_STARTED"})
        Phase.objects.get_or_create(nom="Dossier & Entretiens", defaults={"date_debut":today, "ordre":5, "statut":"NOT_STARTED"})

        # modules (demo)
        modules = [
            ("M1.1_GL","Maths 1","S1","commun"),
            ("M1.2_GL","Prog 1","S1","commun"),
            ("M2.1_GL","Algo 2","S2","commun"),
            ("M2.2_RC","Réseaux 2","S2","commun"),
            ("SP_GL","Spécifique GL","S3","specifique"),
            ("SP_IAD","Spécifique IAD","S3","specifique"),
            ("SP_RC","Spécifique RC","S3","specifique"),
        ]
        for code, nom, sem, t in modules:
            Module.objects.get_or_create(code=code, defaults={"nom":nom, "semestre":sem, "type_module":t})

        # places (matrice alignement)
        AlignmentPlace.objects.get_or_create(partenaire=p1, filiere_ensias=gl, filiere_partenaire="CS", annee=today.year,
                                             type_mobilite="EXCHANGE", defaults={"nombre_places":2, "flechee":True})
        AlignmentPlace.objects.get_or_create(partenaire=p1, filiere_ensias=iad, filiere_partenaire="AI", annee=today.year,
                                             type_mobilite="DOUBLE_DEGREE", defaults={"nombre_places":1, "flechee":True})
        AlignmentPlace.objects.get_or_create(partenaire=p2, filiere_ensias=gl, filiere_partenaire="SE", annee=today.year,
                                             type_mobilite="DOUBLE_DEGREE", defaults={"nombre_places":1, "flechee":False})
        AlignmentPlace.objects.get_or_create(partenaire=p2, filiere_ensias=rc, filiere_partenaire="Networks", annee=today.year,
                                             type_mobilite="EXCHANGE", defaults={"nombre_places":2, "flechee":True})

        # étudiants
        students = []
        for i in range(1, 6):
            email = f"student{i}@ensias.ma"
            u = self._user(email, f"Student{i}", "ENSIAS", "STUDENT")
            fil = random.choice([gl, iad, rc])
            s, _ = Student.objects.get_or_create(
                user=u,
                defaults={
                    "cne": f"CNE{i:04d}",
                    "code_apogee": f"APO{i:04d}",
                    "telephone": "0600000000",
                    "filiere": fil,
                    "redoublement_a1": False,
                    "blame": False,
                    "moyenne_a1": 13.5 + random.random(),  # ok seuil
                }
            )
            students.append(s)

        # notes (annee demo)
        annee = "2024/2025"
        all_mods = list(Module.objects.all())
        for s in students:
            for m in all_mods:
                StudentNote.objects.update_or_create(
                    student=s, module=m, annee_univ=annee,
                    defaults={"note": round(10 + random.random()*10, 2)}
                )

        # desiderata (demo)
        places = list(AlignmentPlace.objects.all())
        for s in students:
            des, _ = Desiderata.objects.get_or_create(student=s)
            # 3 choix compatibles (si possible)
            compatible = [pl for pl in places if pl.filiere_ensias_id == s.filiere_id]
            if not compatible:
                continue
            des.statut = "SUBMITTED"
            des.date_soumission = timezone.now()
            des.save()
            DesiderataChoice.objects.filter(desiderata=des).delete()
            for r, pl in enumerate(compatible[:3], start=1):
                DesiderataChoice.objects.create(desiderata=des, place=pl, rank=r)

        self.stdout.write(self.style.SUCCESS("Données de démo créées ✅"))
        self.stdout.write(self.style.SUCCESS(f"Mot de passe commun: {PASS}"))

    def _user(self, email, first, last, role):
        u, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email, "first_name": first, "last_name": last, "role": role},
        )
        if created:
            u.set_password(PASS)
            u.save()
        else:
            # s'assurer du role
            if u.role != role:
                u.role = role
                u.save(update_fields=["role"])
        return u
