# ami/forms.py
from django import forms
from .models import (
    LembagaAkreditasi,
    ProgramStudi,
    Auditor,
    AuditSession,
    PenilaianDiri,
    Audit,
    DokumenPendukung,
    RekomendasiTindakLanjut,
    KategoriKondisi
)

class LembagaAkreditasiForm(forms.ModelForm):
    class Meta:
        model = LembagaAkreditasi
        fields = ['kode', 'nama', 'deskripsi', 'website', 'kontak']
        widgets = {
            'deskripsi': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'kontak': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'kode': forms.TextInput(attrs={'class': 'form-control'}),
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }

class ProgramStudiForm(forms.ModelForm):
    class Meta:
        model = ProgramStudi
        fields = ['lembaga_akreditasi', 'kode', 'nama', 'fakultas', 'jenjang', 'akreditasi', 'tanggal_berdiri']
        widgets = {
            'lembaga_akreditasi': forms.Select(attrs={'class': 'form-control'}),
            'kode': forms.TextInput(attrs={'class': 'form-control'}),
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'fakultas': forms.TextInput(attrs={'class': 'form-control'}),
            'jenjang': forms.Select(attrs={'class': 'form-control'}),
            'akreditasi': forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal_berdiri': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class AuditorForm(forms.ModelForm):
    class Meta:
        model = Auditor
        fields = ['user', 'nip', 'nama_lengkap', 'jabatan', 'unit_kerja', 'nomor_registrasi', 'is_auditor_ketua']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'nip': forms.TextInput(attrs={'class': 'form-control'}),
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control'}),
            'jabatan': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_kerja': forms.TextInput(attrs={'class': 'form-control'}),
            'nomor_registrasi': forms.TextInput(attrs={'class': 'form-control'}),
            'is_auditor_ketua': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AuditSessionForm(forms.ModelForm):
    class Meta:
        model = AuditSession
        fields = ['program_studi', 'tahun_akademik', 'semester', 'tanggal_mulai', 'tanggal_selesai', 'status', 'auditor_ketua', 'auditor_anggota']
        widgets = {
            'program_studi': forms.Select(attrs={'class': 'form-control'}),
            'tahun_akademik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 2023/2024'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'auditor_ketua': forms.Select(attrs={'class': 'form-control'}),
            'auditor_anggota': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class PenilaianDiriForm(forms.ModelForm):
    class Meta:
        model = PenilaianDiri
        fields = ['indikator', 'skor', 'komentar', 'status']
        widgets = {
            'indikator': forms.Select(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'skor': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '4', 'step': '0.01'}),
            'komentar': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['skor', 'deskripsi_kondisi', 'kategori_kondisi', 'komentar']
        widgets = {
            'skor': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '4', 'step': '0.01'}),
            'deskripsi_kondisi': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'kategori_kondisi': forms.Select(attrs={'class': 'form-control'}),
            'komentar': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class DokumenPendukungForm(forms.ModelForm):
    class Meta:
        model = DokumenPendukung
        fields = ['nama', 'file', 'deskripsi']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'deskripsi': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class RekomendasiTindakLanjutForm(forms.ModelForm):
    class Meta:
        model = RekomendasiTindakLanjut
        fields = ['deskripsi', 'prioritas', 'tenggat_waktu', 'status', 'bukti_tindak_lanjut']
        widgets = {
            'deskripsi': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'prioritas': forms.Select(attrs={'class': 'form-control'}),
            'tenggat_waktu': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'bukti_tindak_lanjut': forms.FileInput(attrs={'class': 'form-control'}),
        }