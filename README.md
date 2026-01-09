<<<<<<< HEAD
# Projet_SI-BD
=======
# ENSIAS Mobilité Internationale — Django (MVP exécutable)

## Prérequis
- Python **3.9.x** (recommandé, compatible) / 3.10+
- Django **4.2.24**
- (Optionnel) Git

## Installation (Windows / Linux / macOS)

```bash
# 1) créer venv
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2) installer deps
pip install -r requirements.txt

# 3) migrations
python manage.py makemigrations
python manage.py migrate

# 4) créer superuser (admin Django)
python manage.py createsuperuser

# 5) (optionnel) créer des données de démo (comptes + places + modules + notes)
python manage.py seed_demo

# 6) lancer
python manage.py runserver
```

Ouvrir: http://127.0.0.1:8000

## Comptes démo (si vous avez exécuté `seed_demo`)
- Étudiant: `student1@ensias.ma` / `Pass12345!`
- Responsable Mobilité: `manager@ensias.ma` / `Pass12345!`
- Scolarité: `admin@ensias.ma` / `Pass12345!`
- Direction: `director@ensias.ma` / `Pass12345!`
- Partenaire: `partner@partner.com` / `Pass12345!`

> Le login utilise le champ `username` (par simplicité). Dans les données démo, `username = email`.

## Fonctionnalités incluses (MVP)
- Authentification + multi-rôles (Étudiant, Responsable Mobilité, Scolarité, Direction, Partenaire)
- Dashboards par rôle
- Étudiant: candidature, desiderata, documents, résultats
- Responsable: lancer classement (sélection) + affectation FIFO
- Notifications: inbox + email console
- Import notes (CSV) + export (CSV)
- Admin Django complet pour CRUD référentiels

## Fichiers importants
- `mobility/services/selection.py` : calcul note + classement + FIFO
- `mobility/management/commands/seed_demo.py` : données de démo
- `templates/` : templates Bootstrap 5 (responsive)

## Notes
- Base SQLite par défaut (facile local)
- Pour SMTP réel / API email, modifier `EMAIL_*` dans `ensias_mobility/settings.py`.
>>>>>>> 5c5b88c (first commit)
