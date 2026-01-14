from django.urls import path
from . import views
from . import views_school_admin, views_director

urlpatterns = [
    # student extra pages
    path("student/messages/", views.student_messages, name="student_messages"),
    path("student/calendar/", views.student_calendar, name="student_calendar"),
    path("student/comparison/", views.student_comparison, name="student_comparison"),
    path("student/chatbot/", views.student_chatbot, name="student_chatbot"),
    path("student/chatbot/api/", views.chatbot_api, name="student_chatbot_api"),

    # school admin
    path("school-admin/", views_school_admin.dashboard, name="school_admin_dashboard"),
    path("school-admin/import/", views_school_admin.import_csv, name="school_admin_import"),
    path("school-admin/export/", views_school_admin.export_csv, name="school_admin_export"),
    path("school-admin/documents/", views_school_admin.documents, name="school_admin_documents"),

    # director
    path("director/", views_director.dashboard, name="director_dashboard"),
    path("director/students/", views_director.students_list, name="director_students"),
    path("director/export/", views_director.export_csv, name="director_export"),
]
