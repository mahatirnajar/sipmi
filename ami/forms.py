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
    Kriteria,
    Elemen,
    IndikatorPenilaian,
    SkorIndikator,
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

class IndikatorPenilaianForm(forms.ModelForm):
    """Form untuk model IndikatorPenilaian"""
    class Meta:
        model = IndikatorPenilaian
        fields = [
            'elemen', 'kode', 'deskripsi', 'panduan', 
            'skor_maksimal', 'memiliki_perhitungan_khusus', 'rumus_perhitungan'
        ]
        widgets = {
            'elemen': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'kode': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Contoh: IK1.1.1, IK1.1.2, dst'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Deskripsi indikator penilaian'
            }),
            'panduan': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Panduan untuk penilaian indikator ini'
            }),
            'skor_maksimal': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'step': '0.1',
                'min': '0'
            }),
            'memiliki_perhitungan_khusus': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'rumus_perhitungan': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Jika memiliki perhitungan khusus, masukkan rumusnya di sini'
            })
        }
    
    def __init__(self, *args, **kwargs):
        elemen_id = kwargs.pop('elemen_id', None)
        super().__init__(*args, **kwargs)
        # Filter elemen jika ada parameter elemen_id
        if elemen_id:
            self.fields['elemen'].queryset = Elemen.objects.filter(id=elemen_id)
            self.fields['elemen'].widget.attrs['disabled'] = True
        else:
            self.fields['elemen'].empty_label = "Pilih Elemen"
        # Tambahkan atribut required
        self.fields['kode'].required = True
        self.fields['deskripsi'].required = True
        self.fields['skor_maksimal'].initial = 4.0

class SkorIndikatorForm(forms.ModelForm):
    """Form untuk model SkorIndikator"""
    class Meta:
        model = SkorIndikator
        fields = ['indikator', 'skor', 'deskripsi']
        widgets = {
            'indikator': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'skor': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'step': '0.1',
                'min': '0'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Deskripsi untuk skor ini'
            })
        }
    
    def __init__(self, *args, **kwargs):
        indikator_id = kwargs.pop('indikator_id', None)
        super().__init__(*args, **kwargs)
        # Filter indikator jika ada parameter indikator_id
        if indikator_id:
            self.fields['indikator'].queryset = IndikatorPenilaian.objects.filter(id=indikator_id)
            self.fields['indikator'].widget.attrs['disabled'] = True
        else:
            self.fields['indikator'].empty_label = "Pilih Indikator Penilaian"
        # Tambahkan atribut required
        self.fields['skor'].required = True
        self.fields['deskripsi'].required = True
    
    def clean_skor(self):
        """Validasi skor harus sesuai dengan skor maksimal indikator"""
        skor = self.cleaned_data.get('skor')
        indikator = self.cleaned_data.get('indikator')
        
        if indikator and skor:
            # Pastikan skor tidak melebihi skor maksimal indikator
            if skor > indikator.skor_maksimal:
                raise forms.ValidationError(
                    f"Skor tidak boleh melebihi skor maksimal indikator ({indikator.skor_maksimal})"
                )
        return skor
    
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
        fields = ['indikator', 'skor', 'komentar', 'status']
        widgets = {
            'indikator': forms.Select(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'skor': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '4', 'step': '0.01'}),
            'komentar': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    # def clean_skor(self):
    #     skor = self.cleaned_data.get('skor')
    #     indikator = self.cleaned_data.get('indikator')
        
    #     if skor is not None and indikator:
    #         if skor < 0:
    #             raise forms.ValidationError("Skor tidak boleh kurang dari 0.")
    #         if skor > indikator.skor_maksimal:
    #             raise forms.ValidationError(
    #                 f"Skor tidak boleh melebihi {indikator.skor_maksimal} (skor maksimal untuk indikator ini)."
    #             )
    #     return skor

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