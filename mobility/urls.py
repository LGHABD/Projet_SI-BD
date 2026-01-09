from django.urls import path
from . import views_student, views_manager

urlpatterns = [
    # étudiant
    path("student/candidature/", views_student.candidature, name="student_candidature"),
    path("student/desiderata/", views_student.desiderata, name="student_desiderata"),
    path("student/documents/", views_student.documents, name="student_documents"),
    path("student/results/", views_student.results, name="student_results"),

    # responsable mobilité
    path("manager/run-selection/", views_manager.run_selection, name="manager_run_selection"),
    path("manager/fifo/", views_manager.run_fifo, name="manager_run_fifo"),
    path("manager/stats/", views_manager.stats, name="manager_stats"),
]
