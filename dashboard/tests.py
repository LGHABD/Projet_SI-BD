from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.models import Filiere, Partenaire, Phase
from mobility.models import Student, AlignmentPlace, Affectation


class SmokeTests(TestCase):
    def setUp(self):
        self.filiere = Filiere.objects.create(nom="GL")
        self.partner = Partenaire.objects.create(nom="Uni A", pays="France", email="a@uni.fr")
        self.place = AlignmentPlace.objects.create(
            partenaire=self.partner,
            filiere_ensias=self.filiere,
            filiere_partenaire="CS",
            annee=2024,
            type_mobilite="EXCHANGE",
            nombre_places=1,
        )
        Phase.objects.create(nom="Desiderata", date_debut="2024-01-01", statut="ACTIVE", ordre=1)

        self.student_user = User.objects.create_user(
            username="student@ensias.ma",
            email="student@ensias.ma",
            password="pass",
            role="STUDENT",
        )
        self.student = Student.objects.create(
            user=self.student_user,
            cne="CNE0001",
            code_apogee="APO0001",
            filiere=self.filiere,
        )

        self.manager_user = User.objects.create_user(
            username="manager@ensias.ma",
            email="manager@ensias.ma",
            password="pass",
            role="MOBILITY_MANAGER",
        )
        self.admin_user = User.objects.create_user(
            username="admin@ensias.ma",
            email="admin@ensias.ma",
            password="pass",
            role="SCHOOL_ADMIN",
        )
        self.director_user = User.objects.create_user(
            username="director@ensias.ma",
            email="director@ensias.ma",
            password="pass",
            role="DIRECTOR",
        )
        self.partner_user = User.objects.create_user(
            username="partner@uni.fr",
            email="partner@uni.fr",
            password="pass",
            role="PARTNER",
            partenaire=self.partner,
        )
        Affectation.objects.create(student=self.student, place=self.place)

    def _login(self, user):
        self.client.logout()
        self.client.force_login(user)

    def test_student_routes(self):
        self._login(self.student_user)
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("student_candidature")).status_code, 200)
        self.assertEqual(self.client.get(reverse("student_desiderata")).status_code, 200)
        self.assertEqual(self.client.get(reverse("student_documents")).status_code, 200)
        self.assertEqual(self.client.get(reverse("student_results")).status_code, 200)
        self.assertEqual(self.client.get(reverse("student_messages")).status_code, 200)
        self.assertEqual(self.client.get(reverse("student_chatbot")).status_code, 200)

    def test_manager_routes(self):
        self._login(self.manager_user)
        self.assertEqual(self.client.get(reverse("manager_stats")).status_code, 200)
        self.assertEqual(self.client.get(reverse("manager_partners")).status_code, 200)
        self.assertEqual(self.client.get(reverse("manager_places")).status_code, 200)
        self.assertEqual(self.client.get(reverse("manager_phases")).status_code, 200)
        self.assertEqual(self.client.get(reverse("manager_desiderata_validation")).status_code, 200)
        self.assertEqual(self.client.get(reverse("manager_interviews")).status_code, 200)
        self.assertEqual(self.client.get(reverse("manager_documents")).status_code, 200)
        self.assertEqual(self.client.get(reverse("manager_notifications")).status_code, 200)

    def test_school_admin_routes(self):
        self._login(self.admin_user)
        self.assertEqual(self.client.get(reverse("school_admin_dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("school_admin_import")).status_code, 200)
        self.assertEqual(self.client.get(reverse("school_admin_export")).status_code, 200)
        self.assertEqual(self.client.get(reverse("school_admin_documents")).status_code, 200)

    def test_director_routes(self):
        self._login(self.director_user)
        self.assertEqual(self.client.get(reverse("director_dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("director_students")).status_code, 200)
        self.assertEqual(self.client.get(reverse("director_export")).status_code, 200)

    def test_partner_routes(self):
        self._login(self.partner_user)
        self.assertEqual(self.client.get(reverse("partner_dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("partner_decisions")).status_code, 200)
        self.assertEqual(self.client.get(reverse("partner_documents")).status_code, 200)
        self.assertEqual(self.client.get(reverse("partner_messages")).status_code, 200)
