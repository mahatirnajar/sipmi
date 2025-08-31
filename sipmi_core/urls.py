# sipmi_core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Jadwal Periode ED
    path('jadwal-ed/', views.jadwal_ed_list, name='jadwal_ed_list'),
    path('jadwal-ed/create/', views.jadwal_ed_create, name='jadwal_ed_create'),
    path('jadwal-ed/<int:pk>/update/', views.jadwal_ed_update, name='jadwal_ed_update'),
    path('jadwal-ed/<int:pk>/delete/', views.jadwal_ed_delete, name='jadwal_ed_delete'),

    # Kelola Standar
    path('kelola-standar/', views.kelola_standar_list, name='kelola_standar_list'),
    path('kelola-standar/create/', views.standar_create, name='standar_create'),
    path('kelola-standar/<int:pk>/update/', views.standar_update, name='standar_update'),
    path('kelola-standar/<int:pk>/delete/', views.standar_delete, name='standar_delete'),

    # Form Kriteria ED
    path('form-kriteria/', views.form_kriteria_list, name='form_kriteria_list'),
    path('form-kriteria/create/', views.kriteria_create, name='kriteria_create'),
    path('form-kriteria/<int:pk>/update/', views.kriteria_update, name='kriteria_update'),
    path('form-kriteria/<int:pk>/delete/', views.kriteria_delete, name='kriteria_delete'),

    # Lihat Progress
    path('lihat-progress/', views.lihat_progress, name='lihat_progress'),

    # Jadwal AMI
    path('jadwal-ami/', views.jadwal_ami_list, name='jadwal_ami_list'),
    path('jadwal-ami/create/', views.ami_create, name='ami_create'),
    path('jadwal-ami/<int:pk>/update/', views.ami_update, name='ami_update'),
    path('jadwal-ami/<int:pk>/delete/', views.ami_delete, name='ami_delete'),

    # Penugasan Auditor
    path('penugasan-auditor/', views.penugasan_auditor_list, name='penugasan_auditor_list'),
    path('penugasan-auditor/create/', views.penugasan_create, name='penugasan_create'),
    path('penugasan-auditor/<int:pk>/update/', views.penugasan_update, name='penugasan_update'),
    path('penugasan-auditor/<int:pk>/delete/', views.penugasan_delete, name='penugasan_delete'),

    # Kelola Auditor
    path('kelola-auditor/', views.kelola_auditor_list, name='kelola_auditor_list'),
    path('kelola-auditor/create/', views.auditor_create, name='auditor_create'),
    path('kelola-auditor/<int:pk>/update/', views.auditor_update, name='auditor_update'),
    path('kelola-auditor/<int:pk>/delete/', views.auditor_delete, name='auditor_delete'),

    # Kelola Auditi
    path('kelola-auditi/', views.kelola_auditi_list, name='kelola_auditi_list'),
    path('kelola-auditi/create/', views.auditi_create, name='auditi_create'),
    path('kelola-auditi/<int:pk>/update/', views.auditi_update, name='auditi_update'),
    path('kelola-auditi/<int:pk>/delete/', views.auditi_delete, name='auditi_delete'),

    # Kelola Password User
    path('kelola-password/', views.kelola_password, name='kelola_password'),
    # Add specific password reset URLs using Django's built-in views if needed
]
