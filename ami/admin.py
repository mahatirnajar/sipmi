from django.contrib import admin
from .models import (
    LembagaAkreditasi,
    Kriteria,
    Elemen,
    ProgramStudi,
    Auditor,
    AuditSession,
    PenilaianDiri,
    Audit,
    DokumenPendukung,
    CatatanAudit,
    RekomendasiTindakLanjut
)

# ----------------------------
# Kelas Admin untuk LembagaAkreditasi
# ----------------------------
@admin.register(LembagaAkreditasi)
class LembagaAkreditasiAdmin(admin.ModelAdmin):
    list_display = ('kode', 'nama', 'website')
    search_fields = ('kode', 'nama', 'deskripsi')
    list_filter = ('nama',)
    ordering = ['nama']
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('kode', 'nama')
        }),
        ('Detail Lembaga', {
            'fields': ('deskripsi', 'website', 'kontak'),
            'classes': ('collapse',)
        }),
    )

# ----------------------------
# Kelas Admin untuk Kriteria
# ----------------------------
@admin.register(Kriteria)
class KriteriaAdmin(admin.ModelAdmin):
    list_display = ('kode', 'nama', 'lembaga_akreditasi')
    search_fields = ('kode', 'nama', 'lembaga_akreditasi__nama')
    list_filter = ('lembaga_akreditasi',)
    ordering = ['lembaga_akreditasi', 'kode']
    raw_id_fields = ('lembaga_akreditasi',)
    fieldsets = (
        ('Informasi Kriteria', {
            'fields': ('lembaga_akreditasi', 'kode', 'nama')
        }),
        ('Deskripsi', {
            'fields': ('deskripsi',),
            'classes': ('collapse',)
        }),
    )

# ----------------------------
# Kelas Admin untuk Elemen
# ----------------------------
@admin.register(Elemen)
class ElemenAdmin(admin.ModelAdmin):
    list_display = ('kode', 'nama', 'kriteria')
    search_fields = ('kode', 'nama', 'kriteria__nama', 'kriteria__lembaga_akreditasi__nama')
    list_filter = ('kriteria__lembaga_akreditasi', 'kriteria',)
    ordering = ['kriteria__lembaga_akreditasi', 'kriteria__kode', 'kode']
    raw_id_fields = ('kriteria',)
    list_select_related = ('kriteria', 'kriteria__lembaga_akreditasi')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('kriteria', 'kriteria__lembaga_akreditasi')

# ----------------------------
# Kelas Admin untuk ProgramStudi
# ----------------------------
@admin.register(ProgramStudi)
class ProgramStudiAdmin(admin.ModelAdmin):
    list_display = ('kode', 'nama', 'jenjang', 'fakultas', 'lembaga_akreditasi')
    search_fields = ('kode', 'nama', 'fakultas', 'lembaga_akreditasi__nama')
    list_filter = ('jenjang', 'lembaga_akreditasi')
    ordering = ['kode']
    raw_id_fields = ('lembaga_akreditasi',)
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('lembaga_akreditasi', 'kode', 'nama', 'jenjang')
        }),
        ('Detail Program Studi', {
            'fields': ('fakultas', 'akreditasi', 'tanggal_akreditasi'),
            'classes': ('collapse',)
        }),
    )

# ----------------------------
# Kelas Admin untuk Auditor
# ----------------------------
@admin.register(Auditor)
class AuditorAdmin(admin.ModelAdmin):
    list_display = ('nama_lengkap', 'nuptk', 'jabatan', 'unit_kerja', 'is_auditor_ketua')
    search_fields = ('nama_lengkap', 'nuptk', 'jabatan', 'unit_kerja', 'user__username')
    list_filter = ('is_auditor_ketua', 'unit_kerja')
    ordering = ['nama_lengkap']
    raw_id_fields = ('user',)
    fieldsets = (
        ('Informasi Pengguna', {
            'fields': ('user', 'nuptk', 'nama_lengkap')
        }),
        ('Detail Auditor', {
            'fields': ('jabatan', 'unit_kerja', 'nomor_registrasi', 'is_auditor_ketua'),
            'classes': ('collapse',)
        }),
    )

# ----------------------------
# Kelas Admin untuk AuditSession
# ----------------------------
@admin.register(AuditSession)
class AuditSessionAdmin(admin.ModelAdmin):
    list_display = ('program_studi', 'tahun_akademik', 'semester', 'tanggal_mulai_penilaian_mandiri', 'status', 'auditor_ketua')
    search_fields = ('program_studi__nama', 'tahun_akademik', 'auditor_ketua__nama_lengkap')
    list_filter = ('tahun_akademik', 'semester', 'status', 'program_studi__lembaga_akreditasi')
    ordering = ['-tanggal_mulai_penilaian_mandiri']
    raw_id_fields = ('program_studi', 'auditor_ketua')
    filter_horizontal = ('auditor_anggota',)
    date_hierarchy = 'tanggal_mulai_penilaian_mandiri'
    list_select_related = ('program_studi', 'auditor_ketua')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('program_studi', 'auditor_ketua')

# ----------------------------
# Kelas Admin untuk PenilaianDiri
# ----------------------------
@admin.register(PenilaianDiri)
class PenilaianDiriAdmin(admin.ModelAdmin):
    list_display = ('audit_session', 'elemen', 'skor', 'status', 'tanggal_penilaian')
    search_fields = ('audit_session__program_studi__nama', 'elemen__kode', 'elemen__deskripsi')
    list_filter = ('status', 'audit_session__tahun_akademik', 'audit_session__semester')
    ordering = ['audit_session', 'elemen__kode']
    raw_id_fields = ('audit_session', 'elemen')
    list_select_related = ('audit_session', 'audit_session__program_studi', 'elemen')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('audit_session', 'audit_session__program_studi', 'elemen')

# ----------------------------
# Kelas Admin untuk Audit
# ----------------------------
@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('penilaian_diri', 'skor', 'kategori_kondisi', 'auditor', 'tanggal_audit')
    search_fields = ('penilaian_diri__elemen__kode', 'penilaian_diri__elemen__deskripsi', 'auditor__nama_lengkap')
    list_filter = ('kategori_kondisi', 'auditor')
    ordering = ['penilaian_diri__elemen__kode']
    raw_id_fields = ('penilaian_diri', 'auditor')
    list_select_related = ('penilaian_diri', 'penilaian_diri__audit_session', 'penilaian_diri__elemen', 'auditor')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('penilaian_diri', 'penilaian_diri__audit_session', 'penilaian_diri__elemen', 'auditor')

# ----------------------------
# Kelas Admin untuk DokumenPendukung
# ----------------------------
@admin.register(DokumenPendukung)
class DokumenPendukungAdmin(admin.ModelAdmin):
    list_display = ('nama', 'penilaian_diri', 'tanggal_upload')
    search_fields = ('nama', 'deskripsi', 'penilaian_diri__elemen__kode')
    list_filter = ('tanggal_upload',)
    ordering = ['-tanggal_upload']
    raw_id_fields = ('penilaian_diri',)
    list_select_related = ('penilaian_diri', 'penilaian_diri__elemen')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('penilaian_diri', 'penilaian_diri__elemen')

# ----------------------------
# Kelas Admin untuk CatatanAudit
# ----------------------------
@admin.register(CatatanAudit)
class CatatanAuditAdmin(admin.ModelAdmin):
    list_display = ('audit', 'auditor', 'tanggal_catatan')
    search_fields = ('catatan', 'audit__penilaian_diri__elemen__kode', 'auditor__nama_lengkap')
    list_filter = ('tanggal_catatan',)
    ordering = ['-tanggal_catatan']
    raw_id_fields = ('audit', 'auditor', 'dibalas_ke')
    list_select_related = ('audit', 'audit__penilaian_diri', 'audit__penilaian_diri__elemen', 'auditor')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('audit', 'audit__penilaian_diri', 'audit__penilaian_diri__elemen', 'auditor')

# ----------------------------
# Kelas Admin untuk RekomendasiTindakLanjut
# ----------------------------
@admin.register(RekomendasiTindakLanjut)
class RekomendasiTindakLanjutAdmin(admin.ModelAdmin):
    list_display = ('audit', 'prioritas', 'status', 'tenggat_waktu')
    search_fields = ('deskripsi', 'audit__penilaian_diri__elemen__kode')
    list_filter = ('prioritas', 'status', 'tenggat_waktu')
    ordering = ['tenggat_waktu']
    raw_id_fields = ('audit',)
    list_select_related = ('audit', 'audit__penilaian_diri', 'audit__penilaian_diri__elemen')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('audit', 'audit__penilaian_diri', 'audit__penilaian_diri__elemen')