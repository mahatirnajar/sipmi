# sipmi_core/admin.py
from django.contrib import admin
from .models import ProgramStudi, Standar, KriteriaED, JadwalED, Auditor, JadwalAMI, PenugasanAuditor

@admin.register(ProgramStudi)
class ProgramStudiAdmin(admin.ModelAdmin):
    list_display = ('nama',)
    search_fields = ('nama',)

@admin.register(Standar)
class StandarAdmin(admin.ModelAdmin):
    list_display = ('nama', 'deskripsi')
    search_fields = ('nama',)

@admin.register(KriteriaED)
class KriteriaEDAdmin(admin.ModelAdmin):
    list_display = ('standar', 'nama', 'bobot', 'status')
    list_filter = ('standar', 'status')
    search_fields = ('nama',)

@admin.register(JadwalED)
class JadwalEDAdmin(admin.ModelAdmin):
    list_display = ('program_studi', 'periode', 'tanggal_mulai', 'tanggal_selesai', 'status')
    list_filter = ('program_studi', 'status')
    search_fields = ('periode',)

@admin.register(Auditor)
class AuditorAdmin(admin.ModelAdmin):
    list_display = ('user', 'nip', 'jabatan', 'sertifikat_status', 'status')
    list_filter = ('status', 'sertifikat_status')
    search_fields = ('user__username', 'nip')

@admin.register(JadwalAMI)
class JadwalAMIAdmin(admin.ModelAdmin):
    list_display = ('program_studi', 'auditor', 'tanggal', 'status')
    list_filter = ('program_studi', 'auditor', 'status')
    search_fields = ('program_studi__nama', 'auditor__user__username')

@admin.register(PenugasanAuditor)
class PenugasanAuditorAdmin(admin.ModelAdmin):
    list_display = ('auditor', 'program_studi', 'periode', 'status')
    list_filter = ('auditor', 'program_studi', 'status')
    search_fields = ('periode',)
