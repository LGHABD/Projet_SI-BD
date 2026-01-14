# ENSIAS Mobilite Internationale (Django 4.2)

Projet Django 4.2 (Python 3.9) avec SQLite. Interface multi-roles, Bootstrap 5 + Bootstrap Icons.

## Prerequis
- Python 3.9+
- Django 4.2.x

## Installation
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Ouvrir: http://127.0.0.1:8000

## Comptes demo (seed_demo)
- Etudiant: `student1@ensias.ma` / `Pass12345!`
- Responsable Mobilite: `manager@ensias.ma` / `Pass12345!`
- Scolarite: `admin@ensias.ma` / `Pass12345!`
- Direction: `director@ensias.ma` / `Pass12345!`
- Partenaire: `partner@unia.fr` / `Pass12345!`

Admin Django:
- http://127.0.0.1:8000/admin
- `root` / `Pass12345!`

## Commandes utiles
```bash
python manage.py seed_demo
python manage.py import_notes path/to/notes.csv
python manage.py export_students path/to/students.csv
```

## Fonctionnalites principales
- Etudiant: dashboard, candidature, desiderata, documents, resultats, messages, chatbot
- Responsable: partenaires, places, phases, selection, affectation, dossiers, notifications
- Scolarite: dashboard, import/export CSV, validation documents
- Direction: KPIs, liste etudiants, export CSV
- Partenaire: dashboard, decisions, dossiers, messages

## Notes
- Base SQLite par defaut
- Email en mode console (voir `ensias_mobility/settings.py`)
