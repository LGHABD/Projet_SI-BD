from django.contrib import admin
from .models import (
    Student, StudentNote, AlignmentPlace,
    Desiderata, DesiderataChoice,
    SelectionResult, Affectation,
    DocumentAdministratif, Entretien
)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("cne", "code_apogee", "filiere", "statut", "redoublement_a1", "blame")
    list_filter = ("filiere", "statut", "redoublement_a1", "blame")
    search_fields = ("cne", "code_apogee", "user__email", "user__username")

admin.site.register(StudentNote)
admin.site.register(AlignmentPlace)
admin.site.register(Desiderata)
admin.site.register(DesiderataChoice)
admin.site.register(SelectionResult)
admin.site.register(Affectation)
admin.site.register(DocumentAdministratif)
admin.site.register(Entretien)
