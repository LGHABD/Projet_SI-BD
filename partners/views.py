from django.shortcuts import render
from accounts.decorators import role_required
from mobility.models import Affectation

@role_required("PARTNER")
def decisions(request):
    # MVP: page vide + instructions. (Pour relier User(partner) -> Partenaire, ajouter un champ FK dans User ou un modèle Profile)
    return render(request, "partners/decisions.html", {"affectations": Affectation.objects.select_related("place","place__partenaire","student")[:50]})
