from django.urls import path
from . import views

app_name = 'ami'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Lembaga Akreditasi
    path('lembaga-akreditasi/', views.lembaga_akreditasi_list, name='lembaga_akreditasi_list'),
    path('lembaga/<int:pk>/', views.lembaga_akreditasi_detail, name='lembaga_akreditasi_detail'),
    path('lembaga-akreditasi/create/', views.lembaga_akreditasi_create, name='lembaga_akreditasi_create'),
    path('lembaga-akreditasi/<int:pk>/edit/', views.lembaga_akreditasi_update, name='lembaga_akreditasi_update'),
    path('lembaga-akreditasi/<int:pk>/delete/', views.lembaga_akreditasi_delete, name='lembaga_akreditasi_delete'),

    # Program Studi
    path('program-studi/', views.program_studi_list, name='program_studi_list'),
    path('program-studi/create/', views.program_studi_create, name='program_studi_create'),
    path('program-studi/<int:pk>/', views.program_studi_detail, name='program_studi_detail'),
    path('program-studi/<int:pk>/edit/', views.program_studi_update, name='program_studi_update'),
    path('program-studi/<int:pk>/delete/', views.program_studi_delete, name='program_studi_delete'),

    #Koordinator Progam Studi
    path('koordinator/', views.koordinator_list, name='koordinator_list'),
    path('koordinator/create/', views.koordinator_create, name='koordinator_create'),
    path('koordinator/<int:pk>/', views.koordinator_detail, name='koordinator_detail'),
    path('koordinator/<int:pk>/update/', views.koordinator_update, name='koordinator_update'),
    path('koordinator/<int:pk>/delete/', views.koordinator_delete, name='koordinator_delete'),

    # Kriteria URLs
    path('kriteria/', views.kriteria_list, name='kriteria_list'),
    path('kriteria/add/<int:lembaga_id>', views.kriteria_create, name='kriteria_create'),
    path('kriteria/<int:pk>/edit/', views.kriteria_update, name='kriteria_update'),
    path('kriteria/<int:pk>/', views.kriteria_detail, name='kriteria_detail'),
    path('kriteria/<int:pk>/delete/', views.kriteria_delete, name='kriteria_delete'),
    path('api/lembaga/<int:pk>/', views.get_lembaga_kode, name='api_lembaga_kode'),
    
    # Elemen URLs
    path('kriteria/<int:kriteria_id>/elemen/', views.elemen_list, name='elemen_list'),
    path('elemen/add/', views.elemen_create, name='elemen_create'),
    path('kriteria/<int:kriteria_id>/elemen/add/', views.elemen_create, name='elemen_create_by_kriteria'),
    path('elemen/<int:pk>/edit/', views.elemen_update, name='elemen_update'),
    path('elemen/<int:pk>/', views.elemen_detail, name='elemen_detail'),
    path('elemen/<int:pk>/delete/', views.elemen_delete, name='elemen_delete'),
    
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
    path('penilaian-submit-penilaian-diri/<int:session_id>/', views.submit_penilaian_diri, name='submit_penilaian_diri'),
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
