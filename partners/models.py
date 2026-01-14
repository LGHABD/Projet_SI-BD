from django.db import models
from core.models import Partenaire
from mobility.models import Student, Affectation

class PartnerDecision(models.Model):
    partenaire = models.ForeignKey(Partenaire, on_delete=models.CASCADE)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    affectation = models.ForeignKey(Affectation, on_delete=models.PROTECT)

    class Result(models.TextChoices):
        ACCEPTED = "ACCEPTED", "Accepté"
        REFUSED = "REFUSED", "Refusé"

    resultat = models.CharField(max_length=10, choices=Result.choices)
    decision_partenaire = models.CharField(max_length=20, blank=True)
    date_decision = models.DateTimeField(auto_now_add=True)
    lettre_acceptation = models.FileField(upload_to="lettres/", null=True, blank=True)
    lettre_reponse = models.FileField(upload_to="lettres/", null=True, blank=True)

    def __str__(self):
        return f"{self.partenaire} - {self.student} : {self.resultat}"
