from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dang-ky/', views.register_view, name='register'),
    path('dang-nhap/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('listening/', views.listening_view, name='listening'),
    path('dang-xuat/', views.logout_view, name='logout'),
]
