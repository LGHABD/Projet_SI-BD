from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Étudiant"
        MOBILITY_MANAGER = "MOBILITY_MANAGER", "Responsable Mobilité"
        SCHOOL_ADMIN = "SCHOOL_ADMIN", "Administration (Scolarité)"
        DIRECTOR = "DIRECTOR", "Direction"
        PARTNER = "PARTNER", "Partenaire"

    role = models.CharField(max_length=32, choices=Role.choices)
    
    # Email unique (utile pour login institutionnel)
    email = models.EmailField(unique=True)

    partenaire = models.ForeignKey(
        "core.Partenaire",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"
    @property
    def unread_notifications_count(self):
        # safe si l'app notifications est installée
        return self.notifications.filter(is_read=False).count()
