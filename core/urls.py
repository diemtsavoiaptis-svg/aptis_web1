from django.urls import path
from . import views
from . import listening_ui

urlpatterns = [
    path("listening/part-2/may-gioi/", views.student_part2_gioi_topics, name="student_part2_gioi_topics"),
    path("listening/part-2/may-kem/", views.student_part2_kem_topics, name="student_part2_kem_topics"),
    path("listening/part-2/may-dot/", views.student_part2_dot_topics, name="student_part2_dot_topics"),

    path("listening/part-2/may-dot/<int:topic_id>/", views.student_part2_dot_page, name="student_part2_dot"),
    path("listening/part-2/may-gioi/<int:topic_id>/", views.student_part2_gioi_page, name="student_part2_gioi"),
    path("dashboard/part-2/may-gioi/<int:topic_id>/", views.admin_part2_gioi_detail, name="admin_part2_gioi_detail"),
    path("dashboard/part-2/may-gioi/", views.admin_part2_gioi_topics, name="admin_part2_gioi_topics"),
    path("dashboard/part-2/<int:topic_id>/", views.admin_part2_topic_detail, name="admin_part2_topic_detail"),
    path("listening/part-4/", views.student_part4_page, name="student_part4"),
    path("listening/part-3/", views.student_part3_page, name="student_part3"),
    path("listening/part-2/", views.student_part2_page, name="student_part2"),
    path("dashboard/part-4/", views.admin_part4_questions, name="admin_part4_questions"),
    path("dashboard/part-3/", views.admin_part3_questions, name="admin_part3_questions"),
    path("dashboard/part-2/", views.admin_part2_questions, name="admin_part2_questions"),
    path("dashboard/students/", views.admin_student_lookup, name="admin_student_lookup"),
path("", views.home, name="home"),
    path("dang-ky/", views.register_view, name="register"),
    path("dang-nhap/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/listening-parts/", views.admin_listening_parts, name="admin_listening_parts"),
    path("dashboard/part-1/", views.admin_part1_questions, name="admin_part1_questions"),
    path("listening/", listening_ui.listening_page, name="listening"),
    path("secure/audio/<int:question_id>/", views.secure_audio_view, name="secure_audio"),
    path("security/event/", views.security_event_view, name="security_event"),
    path("dang-xuat/", views.logout_view, name="logout"),
]
