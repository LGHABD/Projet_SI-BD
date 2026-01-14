from dataclasses import dataclass
from typing import Dict
from django.db import transaction
from django.db.models import Avg

from mobility.models import Student, StudentNote, SelectionResult, Desiderata, Affectation, AlignmentPlace
from notifications.utils import notify_user

# Paramètres par défaut (vous pouvez les modifier via admin / config plus tard)
SEUIL1 = 12.5
SEUIL2 = 13.5
COMMON_WEIGHT = 0.8
SPEC_WEIGHT = 0.2

# Liste "communs" (à adapter à vos codes modules réels)
COMMON_MODULE_CODES = {
    "M1.1_GL","M1.2_GL","M1.3_IAD","M1.6_IAD","M1.7_LC",
    "M2.1_GL","M2.2_RC","M2.6_IAD","M2.7_LC",
}

@dataclass
class SelectionConfig:
    annee_univ: str
    seuil1: float = SEUIL1
    seuil2: float = SEUIL2

def _avg_notes(student: Student, annee_univ: str, module_codes: set) -> float:
    qs = StudentNote.objects.filter(student=student, annee_univ=annee_univ, module__code__in=module_codes)
    return float(qs.aggregate(v=Avg("note"))["v"] or 0.0)

def _avg_specific_notes(student: Student, annee_univ: str) -> float:
    qs = StudentNote.objects.filter(student=student, annee_univ=annee_univ).exclude(module__code__in=COMMON_MODULE_CODES)
    return float(qs.aggregate(v=Avg("note"))["v"] or 0.0)

def compute_selection_note(student: Student, config: SelectionConfig) -> float:
    common = _avg_notes(student, config.annee_univ, COMMON_MODULE_CODES)
    spec = _avg_specific_notes(student, config.annee_univ)
    return round(COMMON_WEIGHT * common + SPEC_WEIGHT * spec, 3)

def pass1_filter(student: Student, config: SelectionConfig) -> bool:
    # simplification des règles d'éligibilité
    if student.redoublement_a1:
        return False
    if student.blame:
        return False
    if student.moyenne_a1 is not None:
        return student.moyenne_a1 > config.seuil1
    # fallback: utiliser la note calculée
    return compute_selection_note(student, config) > config.seuil1

@transaction.atomic
def run_ranking(config: SelectionConfig) -> int:
    eligible = []
    for s in Student.objects.select_related("filiere").all():
        if pass1_filter(s, config):
            eligible.append(s)
        else:
            s.statut = Student.Status.NOT_ELIGIBLE
            s.save(update_fields=["statut"])

    ranked = [(s, compute_selection_note(s, config)) for s in eligible]
    ranked.sort(key=lambda x: x[1], reverse=True)

    for i, (student, note) in enumerate(ranked, start=1):
        SelectionResult.objects.update_or_create(
            student=student,
            defaults={"note_selection": note, "rang": i, "passe_attente": False},
        )
        student.statut = Student.Status.ELIGIBLE
        student.save(update_fields=["statut"])

    return len(ranked)

@transaction.atomic
def fifo_assign(config: SelectionConfig) -> Dict[str, int]:
    ranked = list(SelectionResult.objects.select_related("student").order_by("rang"))
    remaining = {p.id: p.nombre_places for p in AlignmentPlace.objects.all()}

    assigned = 0
    waiting = 0

    for sr in ranked:
        student = sr.student
        try:
            des = student.desiderata
        except Desiderata.DoesNotExist:
            sr.passe_attente = True
            sr.save(update_fields=["passe_attente"])
            waiting += 1
            continue

        if des.statut not in [Desiderata.Status.SUBMITTED, Desiderata.Status.VALID]:
            sr.passe_attente = True
            sr.save(update_fields=["passe_attente"])
            waiting += 1
            continue

        placed = False
        for choice in des.choices.select_related("place", "place__partenaire").all():
            place = choice.place
            if place.filiere_ensias_id != student.filiere_id:
                continue
            if remaining.get(place.id, 0) <= 0:
                continue

            Affectation.objects.update_or_create(student=student, defaults={"place": place})
            remaining[place.id] -= 1

            student.statut = Student.Status.ASSIGNED
            student.save(update_fields=["statut"])

            notify_user(
                student.user,
                "Affectation",
                f"Vous etes affecte a {place.partenaire.nom} ({place.type_mobilite}).",
            )
            assigned += 1
            placed = True
            break

        if not placed:
            sr.passe_attente = True
            sr.save(update_fields=["passe_attente"])
            waiting += 1

    return {"assigned": assigned, "waiting": waiting}
