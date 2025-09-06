from django.urls import path
from . import views

app_name = 'ami'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Lembaga Akreditasi
    path('lembaga-akreditasi/', views.lembaga_akreditasi_list, name='lembaga_akreditasi_list'),
    path('lembaga-akreditasi/create/', views.lembaga_akreditasi_create, name='lembaga_akreditasi_create'),
    path('lembaga-akreditasi/<int:pk>/edit/', views.lembaga_akreditasi_update, name='lembaga_akreditasi_update'),
    path('lembaga-akreditasi/<int:pk>/delete/', views.lembaga_akreditasi_delete, name='lembaga_akreditasi_delete'),

    # Program Studi
    path('program-studi/', views.program_studi_list, name='program_studi_list'),
    path('program-studi/create/', views.program_studi_create, name='program_studi_create'),
    path('program-studi/<int:pk>/', views.program_studi_detail, name='program_studi_detail'),
    path('program-studi/<int:pk>/edit/', views.program_studi_update, name='program_studi_update'),
    path('program-studi/<int:pk>/delete/', views.program_studi_delete, name='program_studi_delete'),

    # Auditor
    path('auditor/', views.auditor_list, name='auditor_list'),
    path('auditor/create/', views.auditor_create, name='auditor_create'),
    path('auditor/<int:pk>/edit/', views.auditor_update, name='auditor_update'),

    # Audit Session
    path('audit-session/', views.audit_session_list, name='audit_session_list'),
    path('audit-session/create/', views.audit_session_create, name='audit_session_create'),
    path('audit-session/<int:pk>/', views.audit_session_detail, name='audit_session_detail'),
    path('audit-session/<int:pk>/edit/', views.audit_session_update, name='audit_session_update'),
    path('audit-session/<int:pk>/delete/', views.audit_session_delete, name='audit_session_delete'),

    # Penilaian Diri
    path('penilaian-diri/<int:session_id>/', views.penilaian_diri_list, name='penilaian_diri_list'),
    path('penilaian-diri/<int:session_id>/create/', views.penilaian_diri_create, name='penilaian_diri_create'),
    path('penilaian-diri/<int:pk>/edit/', views.penilaian_diri_update, name='penilaian_diri_update'),

    # Audit
    path('audit/<int:session_id>/', views.audit_list, name='audit_list'),
    path('audit/<int:pk>/edit/', views.audit_update, name='audit_update'),

    # Dokumen Pendukung
    path('dokumen-pendukung/<int:penilaian_id>/create/', views.dokumen_pendukung_create, name='dokumen_pendukung_create'),
    path('dokumen-pendukung/<int:pk>/delete/', views.dokumen_pendukung_delete, name='dokumen_pendukung_delete'),

    # Rekomendasi Tindak Lanjut
    path('rekomendasi/<int:session_id>/', views.rekomendasi_tindak_lanjut_list, name='rekomendasi_tindak_lanjut_list'),
    path('rekomendasi/<int:pk>/edit/', views.rekomendasi_tindak_lanjut_update, name='rekomendasi_tindak_lanjut_update'),

    # Laporan Audit
    path('laporan/<int:session_id>/', views.laporan_audit, name='laporan_audit'),
]
