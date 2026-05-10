from django.urls import path
from . import views
from . import listening_ui

urlpatterns = [
    path("dashboard/students/", views.admin_student_lookup, name="admin_student_lookup"),
    path("", views.home, name="home"),
    path("dang-ky/", views.register_view, name="register"),
    path("dang-nhap/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/listening-parts/", views.admin_listening_parts, name="admin_listening_parts"),
    path("dashboard/part-1/", views.admin_part1_questions, name="admin_part1_questions"),    path("listening/", listening_ui.listening_page, name="listening"),
    path("secure/audio/<int:question_id>/", views.secure_audio_view, name="secure_audio"),
    path("security/event/", views.security_event_view, name="security_event"),
    path("dang-xuat/", views.logout_view, name="logout"),
]
