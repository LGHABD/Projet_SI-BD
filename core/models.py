from django.db import models

class Filiere(models.Model):
    nom = models.CharField(max_length=120, unique=True)
    pool = models.CharField(max_length=50, blank=True)
    seuil_eligibilite = models.FloatField(default=12.5)
    pourcentage_modules_communs = models.FloatField(default=0.8)
    pourcentage_modules_specifiques = models.FloatField(default=0.2)

    def __str__(self):
        return self.nom

class Partenaire(models.Model):
    nom = models.CharField(max_length=160, unique=True)
    pays = models.CharField(max_length=80)
    email = models.EmailField()
    contact_name = models.CharField(max_length=120, blank=True)
    active = models.BooleanField(default=True)
    ville = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.pays})"

class Phase(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "NOT_STARTED", "Non démarrée"
        ACTIVE = "ACTIVE", "En cours"
        CLOSED = "CLOSED", "Clôturée"

    nom = models.CharField(max_length=120, unique=True)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    ordre = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nom

class Module(models.Model):
    code = models.CharField(max_length=40, primary_key=True)
    nom = models.CharField(max_length=160)
    semestre = models.CharField(max_length=10)  # S1/S2/S3
    type_module = models.CharField(max_length=40)  # commun/spécifique

    def __str__(self):
        return f"{self.code} - {self.nom}"
