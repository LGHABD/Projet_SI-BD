from django import forms
from core.models import Partenaire, Phase
from mobility.models import AlignmentPlace, Entretien


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partenaire
        fields = ["nom", "pays", "ville", "email", "contact_name", "active"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "pays": forms.TextInput(attrs={"class": "form-control"}),
            "ville": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "contact_name": forms.TextInput(attrs={"class": "form-control"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PhaseForm(forms.ModelForm):
    class Meta:
        model = Phase
        fields = ["nom", "date_debut", "date_fin", "statut", "ordre"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "date_debut": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "date_fin": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
            "ordre": forms.NumberInput(attrs={"class": "form-control"}),
        }


class AlignmentPlaceForm(forms.ModelForm):
    class Meta:
        model = AlignmentPlace
        fields = [
            "partenaire",
            "filiere_ensias",
            "filiere_partenaire",
            "annee",
            "type_mobilite",
            "nombre_places",
            "flechee",
            "open_to_all",
        ]
        widgets = {
            "partenaire": forms.Select(attrs={"class": "form-select"}),
            "filiere_ensias": forms.Select(attrs={"class": "form-select"}),
            "filiere_partenaire": forms.TextInput(attrs={"class": "form-control"}),
            "annee": forms.NumberInput(attrs={"class": "form-control"}),
            "type_mobilite": forms.Select(attrs={"class": "form-select"}),
            "nombre_places": forms.NumberInput(attrs={"class": "form-control"}),
            "flechee": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "open_to_all": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Entretien
        fields = ["date_entretien", "motivation", "capacite_financiere", "decision"]
        widgets = {
            "date_entretien": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "motivation": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "capacite_financiere": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "decision": forms.Select(attrs={"class": "form-select"}),
        }


class NotificationForm(forms.Form):
    ROLE_CHOICES = [
        ("STUDENT", "Etudiants"),
        ("PARTNER", "Partenaires"),
    ]
    recipient_role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    body = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))
    send_email = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
