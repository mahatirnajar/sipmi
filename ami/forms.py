# ami/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import (
    LembagaAkreditasi,
    ProgramStudi,
    Auditor,
    AuditSession,
    PenilaianDiri,
    Audit,
    DokumenPendukung,
    RekomendasiTindakLanjut,
    Kriteria,
    Elemen,
    KoordinatorProgramStudi,
    KategoriKondisi,
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
        fields = ['lembaga_akreditasi', 'kode', 'nama', 'fakultas', 'jenjang', 'akreditasi', 'tanggal_akreditasi']
        widgets = {
            'lembaga_akreditasi': forms.Select(attrs={'class': 'form-control'}),
            'kode': forms.TextInput(attrs={'class': 'form-control'}),
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'fakultas': forms.Select(attrs={'class': 'form-control'}),
            'jenjang': forms.Select(attrs={'class': 'form-control'}),
            'akreditasi': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_akreditasi': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class KriteriaForm(forms.ModelForm):
    """Form untuk model Kriteria"""
    class Meta:
        model = Kriteria
        fields = ['lembaga_akreditasi', 'kode', 'nama', 'deskripsi']
        widgets = {
            'lembaga_akreditasi': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'kode': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Contoh: K1, K2, dst'
            }),
            'nama': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Nama kriteria'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Deskripsi lengkap kriteria'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tambahkan placeholder untuk field yang membutuhkan
        if 'lembaga_akreditasi' in self.fields:
            self.fields['lembaga_akreditasi'].empty_label = "Pilih Lembaga Akreditasi"
        # Tambahkan atribut required
        self.fields['kode'].required = True
        self.fields['nama'].required = True

class ElemenForm(forms.ModelForm):
    """Form untuk model Elemen"""
    class Meta:
        model = Elemen
        fields = ['kriteria', 'kode', 'nama', 'deskripsi']
        widgets = {
            'kriteria': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'kode': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Contoh: KE1.1, KE1.2, dst'
            }),
            'nama': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Nama elemen'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Deskripsi lengkap elemen'
            })
        }
    
    def __init__(self, *args, **kwargs):
        kriteria_id = kwargs.pop('kriteria_id', None)
        super().__init__(*args, **kwargs)
        # Filter kriteria jika ada parameter kriteria_id
        if kriteria_id:
            self.fields['kriteria'].queryset = Kriteria.objects.filter(id=kriteria_id)
            self.fields['kriteria'].widget.attrs['disabled'] = True
        else:
            self.fields['kriteria'].empty_label = "Pilih Kriteria"
        # Tambahkan atribut required
        self.fields['kode'].required = True
        self.fields['nama'].required = True

class KoordinatorProgramStudiForm(forms.ModelForm):
    class Meta:
        model = KoordinatorProgramStudi
        fields = ['nuptk', 'nama_lengkap', 'program_studi']
        widgets = {
            'nuptk': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Masukkan NUPTK'
            }),
            'nama_lengkap': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Masukkan nama lengkap'
            }),
            'program_studi': forms.Select(attrs={
                'class': 'form-select mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
        }

    def clean_nuptk(self):
        """Validasi NUPTK harus unik"""
        nuptk = self.cleaned_data['nuptk']
        if User.objects.filter(username=nuptk).exists():
            raise forms.ValidationError("NUPTK Sudah Terdaftar.")
        return nuptk
class AuditorForm(forms.ModelForm):
    class Meta:
        model = Auditor
        fields = ['nuptk', 'nama_lengkap', 'jabatan', 'unit_kerja', 'nomor_registrasi', 'is_auditor_ketua']
        widgets = {
            'nuptk': forms.TextInput(attrs={'class': 'form-control'}),
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control'}),
            'jabatan': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_kerja': forms.TextInput(attrs={'class': 'form-control'}),
            'nomor_registrasi': forms.TextInput(attrs={'class': 'form-control'}),
            'is_auditor_ketua': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_nuptk(self):
        """Validasi NUPTK harus unik"""
        nuptk = self.cleaned_data['nuptk']
        if User.objects.filter(username=nuptk).exists():
            raise forms.ValidationError("NUPTK Sudah Terdaftar.")
        return nuptk


class AuditSessionForm(forms.ModelForm):
    class Meta:
        model = AuditSession
        fields = ['program_studi', 'tahun_akademik', 'semester', 'tanggal_mulai_penilaian_mandiri', 'tanggal_selesai_penilaian_mandiri','tanggal_selesai_penilian_auditor', 'status', 'auditor_ketua', 'auditor_anggota']
        widgets = {
            'program_studi': forms.Select(attrs={'class': 'form-control'}),
            'tahun_akademik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 2023/2024'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_mulai_penilaian_mandiri': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tanggal_selesai_penilaian_mandiri': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tanggal_selesai_penilian_auditor': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'auditor_ketua': forms.Select(attrs={'class': 'form-control'}),
            'auditor_anggota': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class PenilaianDiriForm(forms.ModelForm):
    class Meta:
        model = PenilaianDiri
        fields = ['elemen', 'skor', 'komentar', 'status']
        widgets = {
            'elemen': forms.Select(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'skor': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '4', 'step': '0.01'}),
            'komentar': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_skor(self):
        skor = self.cleaned_data.get('skor')
        elemen = self.cleaned_data.get('elemen')
        
        if skor is not None and elemen:
            if skor < 0:
                raise forms.ValidationError("Skor tidak boleh kurang dari 0.")
            if skor > elemen.skor_maksimal:
                raise forms.ValidationError(
                    f"Skor tidak boleh melebihi {elemen.skor_maksimal} (skor maksimal untuk indikator ini)."
                )
        return skor

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