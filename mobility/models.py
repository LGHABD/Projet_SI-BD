from django.db import models
from django.conf import settings
from core.models import Filiere, Partenaire, Module

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    cne = models.CharField(max_length=20, unique=True)
    code_apogee = models.CharField(max_length=20, unique=True)
    telephone = models.CharField(max_length=30, blank=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.PROTECT)

    redoublement_a1 = models.BooleanField(default=False)
    blame = models.BooleanField(default=False)
    moyenne_a1 = models.FloatField(null=True, blank=True)
    moyenne_s3 = models.FloatField(null=True, blank=True)

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Brouillon"
        ELIGIBLE = "ELIGIBLE", "Éligible"
        NOT_ELIGIBLE = "NOT_ELIGIBLE", "Non éligible"
        DESIDERATA_SUBMITTED = "DESIDERATA_SUBMITTED", "Desiderata soumis"
        ASSIGNED = "ASSIGNED", "Affecté"
        INTERVIEW = "INTERVIEW", "Entretien"
        SENT_TO_PARTNER = "SENT_TO_PARTNER", "Envoyé partenaire"
        ACCEPTED = "ACCEPTED", "Accepté"
        REFUSED = "REFUSED", "Refusé"

    statut = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)

    def __str__(self):
        return f"{self.cne} - {self.user.get_full_name() or self.user.username}"

class StudentNote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="notes")
    module = models.ForeignKey(Module, on_delete=models.PROTECT)
    annee_univ = models.CharField(max_length=9)  # ex: 2024/2025
    note = models.FloatField()

    class Meta:
        unique_together = [("student", "module", "annee_univ")]

class AlignmentPlace(models.Model):
    class MobilityType(models.TextChoices):
        EXCHANGE = "EXCHANGE", "Échange"
        DOUBLE_DEGREE = "DOUBLE_DEGREE", "Double diplôme"

    partenaire = models.ForeignKey(Partenaire, on_delete=models.CASCADE, related_name="places")
    filiere_ensias = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    filiere_partenaire = models.CharField(max_length=120)
    annee = models.PositiveIntegerField()
    type_mobilite = models.CharField(max_length=20, choices=MobilityType.choices)
    nombre_places = models.PositiveIntegerField(default=0)
    flechee = models.BooleanField(default=False)
    open_to_all = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.partenaire} - {self.filiere_ensias} - {self.type_mobilite} ({self.nombre_places})"

class Desiderata(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="desiderata")
    date_soumission = models.DateTimeField(null=True, blank=True)

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Brouillon"
        SUBMITTED = "SUBMITTED", "Soumis"
        VALID = "VALID", "Validé"
        INVALID = "INVALID", "Refusé"
        RECTIFICATION = "RECTIFICATION", "En rectification"

    statut = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="validated_desiderata",
    )
    validated_at = models.DateTimeField(null=True, blank=True)

class DesiderataChoice(models.Model):
    desiderata = models.ForeignKey(Desiderata, on_delete=models.CASCADE, related_name="choices")
    place = models.ForeignKey(AlignmentPlace, on_delete=models.PROTECT)
    rank = models.PositiveIntegerField()

    class Meta:
        unique_together = [("desiderata", "rank")]
        ordering = ["rank"]

class SelectionResult(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="selection_result")
    note_selection = models.FloatField(null=True, blank=True)
    rang = models.PositiveIntegerField(null=True, blank=True)
    passe_attente = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Affectation(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="affectation")
    place = models.ForeignKey(AlignmentPlace, on_delete=models.PROTECT)

    class Status(models.TextChoices):
        PROVISOIRE = "PROVISOIRE", "Provisoire"
        DEFINITIVE = "DEFINITIVE", "Définitive"
        DESISTE = "DESISTE", "Désisté"

    statut = models.CharField(max_length=20, choices=Status.choices, default=Status.PROVISOIRE)
    date_affectation = models.DateTimeField(auto_now_add=True)
    decision_partenaire = models.CharField(max_length=20, blank=True)
    lettre_reponse = models.FileField(upload_to="lettres/", null=True, blank=True)

class DocumentAdministratif(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents")

    class DocType(models.TextChoices):
        CONVENTION = "CONVENTION", "Convention"
        RELEVES = "RELEVES", "Relevés"
        CV = "CV", "CV"
        LETTRE_MOTIV = "LETTRE_MOTIV", "Lettre de motivation"
        AUTRE = "AUTRE", "Autre"

    type_doc = models.CharField(max_length=30, choices=DocType.choices)
    fichier = models.FileField(upload_to="docs/")
    date_upload = models.DateTimeField(auto_now_add=True)

    class Validation(models.TextChoices):
        PENDING = "PENDING", "En attente"
        VALID = "VALID", "Validé"
        INVALID = "INVALID", "Refusé"

    statut_validation = models.CharField(max_length=20, choices=Validation.choices, default=Validation.PENDING)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="validated_documents",
    )
    validated_at = models.DateTimeField(null=True, blank=True)

class Entretien(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="entretien")
    date_entretien = models.DateTimeField()
    motivation = models.TextField(blank=True)
    capacite_financiere = models.TextField(blank=True)

    class Decision(models.TextChoices):
        ACCEPT = "ACCEPT", "Valider"
        REFUSE = "REFUSE", "Refuser"
        DESISTE = "DESISTE", "Désistement"

    decision = models.CharField(max_length=10, choices=Decision.choices, null=True, blank=True)
