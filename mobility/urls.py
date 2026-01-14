from django.urls import path
from . import views_student, views_manager

urlpatterns = [
    # student
    path("student/candidature/", views_student.candidature, name="student_candidature"),
    path("student/desiderata/", views_student.desiderata, name="student_desiderata"),
    path("student/documents/", views_student.documents, name="student_documents"),
    path("student/results/", views_student.results, name="student_results"),

    # mobility manager
    path("manager/run-selection/", views_manager.run_selection, name="manager_run_selection"),
    path("manager/fifo/", views_manager.run_fifo, name="manager_run_fifo"),
    path("manager/stats/", views_manager.stats, name="manager_stats"),
    path("manager/partners/", views_manager.partners_list, name="manager_partners"),
    path("manager/partners/<int:pk>/edit/", views_manager.partners_edit, name="manager_partners_edit"),
    path("manager/partners/<int:pk>/delete/", views_manager.partners_delete, name="manager_partners_delete"),
    path("manager/places/", views_manager.places_list, name="manager_places"),
    path("manager/places/<int:pk>/edit/", views_manager.places_edit, name="manager_places_edit"),
    path("manager/places/<int:pk>/delete/", views_manager.places_delete, name="manager_places_delete"),
    path("manager/phases/", views_manager.phases_list, name="manager_phases"),
    path("manager/phases/<int:pk>/edit/", views_manager.phases_edit, name="manager_phases_edit"),
    path("manager/phases/<int:pk>/activate/", views_manager.phases_activate, name="manager_phases_activate"),
    path("manager/desiderata/", views_manager.desiderata_validation, name="manager_desiderata_validation"),
    path("manager/interviews/", views_manager.interviews, name="manager_interviews"),
    path("manager/documents/", views_manager.documents, name="manager_documents"),
    path("manager/notifications/", views_manager.notifications, name="manager_notifications"),
]
