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
    """Form untuk model Kriteria dengan kode yang dihasilkan berdasarkan lembaga"""
    nomor = forms.CharField(
        max_length=10,
        required=True,
        label='Nomor Kriteria',
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Contoh: 1, 2, 3',
            'autocomplete': 'off'
        }),
        help_text='Masukkan nomor urut kriteria (hanya angka atau format seperti "K1", "K2")'
    )
    
    class Meta:
        model = Kriteria
        fields = ['lembaga_akreditasi', 'kode', 'nama', 'deskripsi']
        widgets = {
            'lembaga_akreditasi': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'id': 'id_lembaga_akreditasi'
            }),
            'kode': forms.HiddenInput(),  # kode akan diisi otomatis
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

        self.fields['kode'].required = False
        
        # Jika sedang mengedit, coba ekstrak nomor dari kode
        if self.instance.pk and self.instance.kode:
            # Pisahkan kode lembaga dari nomor kriteria
            # Format asumsi: [kode_lembaga]-[nomor] atau [kode_lembaga][nomor]
            lembaga_kode = self.instance.lembaga_akreditasi.kode if self.instance.lembaga_akreditasi else ""
            
            if self.instance.kode.startswith(lembaga_kode):
                # Hapus prefiks lembaga dari kode
                nomor_part = self.instance.kode[len(lembaga_kode):].lstrip('-')
                self.fields['nomor'].initial = nomor_part
            # else:
            #     self.fields['nomor'].initial = self.instance.kode
    
    def clean(self):
        cleaned_data = super().clean()
        lembaga = cleaned_data.get('lembaga_akreditasi')
        nomor = cleaned_data.get('nomor')
        
        # Pastikan lembaga dan nomor ada
        if not lembaga:
            raise forms.ValidationError("Lembaga akreditasi harus dipilih.")
        if not nomor:
            raise forms.ValidationError("Nomor kriteria harus diisi.")
        
        # Generate kode
        cleaned_data['kode'] = f"{lembaga.kode}-{nomor}"
        
        # Validasi keunikan
        existing = Kriteria.objects.filter(
            lembaga_akreditasi=lembaga,
            kode=cleaned_data['kode']
        ).exclude(pk=self.instance.pk if self.instance else None)
        
        if existing.exists():
            raise forms.ValidationError(
                f"Kode '{cleaned_data['kode']}' sudah digunakan untuk lembaga ini. Silakan pilih nomor lain."
            )
        
        return cleaned_data

class ElemenForm(forms.ModelForm):
    """Form untuk model Elemen"""
    class Meta:
        model = Elemen
        fields = '__all__'
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
            }),
            'panduan': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 20,
                'placeholder': 'Panduan Indikator Penilaian '
            }),
            'skor_maksimal': forms.NumberInput(attrs={
                'class':  'form-control',
                'placeholder': 'Skor Maksimal'
            }),
             'status': forms.Select(attrs={
                'class': 'form-select mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
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

    # def clean_nuptk(self):
    #     """Validasi NUPTK harus unik"""
    #     nuptk = self.cleaned_data['nuptk']
    #     if User.objects.filter(username=nuptk).exists():
    #         raise forms.ValidationError("NUPTK Sudah Terdaftar.")
    #     return nuptk
class AuditorForm(forms.ModelForm):
    class Meta:
        model = Auditor
        fields = ['nuptk', 'nama_lengkap', 'jabatan', 'unit_kerja', 'nomor_registrasi', 'is_auditor_ketua', 'status']
        widgets = {
            'nuptk': forms.TextInput(attrs={'class': 'form-control'}),
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control'}),
            'jabatan': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_kerja': forms.TextInput(attrs={'class': 'form-control'}),
            'nomor_registrasi': forms.TextInput(attrs={'class': 'form-control'}),
            'is_auditor_ketua': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={
                'class': 'form-select mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'})
            
        }

    # def clean_nuptk(self):
    #     """Validasi NUPTK harus unik"""
    #     nuptk = self.cleaned_data['nuptk']
    #     if User.objects.filter(username=nuptk).exists():
    #         raise forms.ValidationError("NUPTK Sudah Terdaftar.")
    #     return nuptk


# forms.py
from django import forms
from .models import AuditSession, Auditor

class AuditSessionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter hanya auditor aktif
        aktif_auditor = Auditor.objects.filter(status='aktif')

        self.fields['auditor_ketua'].queryset = aktif_auditor
        self.fields['auditor_anggota'].queryset = aktif_auditor

        # Tambahkan class select2 ke widget
        self.fields['auditor_ketua'].widget.attrs.update({
            'class': 'form-control select2'
        })
        self.fields['auditor_anggota'].widget.attrs.update({
            'class': 'form-control select2-multiple',
            'data-placeholder': 'Pilih auditor anggota...'
        
        })
        ##jika ingin menampilkan nama tanpa nuptk/nidn
        # self.fields['auditor_ketua'].label_from_instance = lambda obj: f"{obj.nama_lengkap}"
        # self.fields['auditor_anggota'].label_from_instance = lambda obj: f"{obj.nama_lengkap}"

    class Meta:
        model = AuditSession
        fields = [
            'program_studi', 'tahun_akademik', 'semester',
            'tanggal_mulai_penilaian_mandiri', 'tanggal_selesai_penilaian_mandiri',
            'tanggal_selesai_penilaian_auditor', 'status',
            'auditor_ketua', 'auditor_anggota'
        ]
        widgets = {
            'program_studi': forms.Select(attrs={'class': 'form-control'}),
            'tahun_akademik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 2023/2024'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_mulai_penilaian_mandiri': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tanggal_selesai_penilaian_mandiri': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tanggal_selesai_penilaian_auditor': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'auditor_ketua': forms.Select(),  # akan diatur di __init__
            'auditor_anggota': forms.SelectMultiple(),  # akan diatur di __init__
        }

class PenilaianDiriForm(forms.ModelForm):
    class Meta:
        model = PenilaianDiri
        fields = ['skor', 'bukti_dokumen', 'komentar']  # Menghapus elemen karena tidak perlu diubah
        widgets = {
            'skor': forms.NumberInput(attrs={'class': 'form-control mt-1 block w-full rounded-md border-black-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'bukti_dokumen': forms.URLInput(attrs={
                'class': 'form-control mt-1 block w-full rounded-md border-black-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'https://drive.google.com/...'
            }),
            'komentar': forms.Textarea(attrs={'rows': 3, 'class': 'form-control mt-1 block w-full rounded-md border-black-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
        }
    
    def clean_bukti_dokumen(self):
        url = self.cleaned_data.get('bukti_dokumen')
        if url:
            # Validasi minimal format URL Google Drive
            if 'drive.google.com' not in url and 'docs.google.com' not in url:
                raise forms.ValidationError(
                    "Harus berupa link Google Drive atau Google Docs yang valid"
                )
        return url

class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['skor', 'deskripsi_kondisi', 'kategori_kondisi']
        widgets = {
            'skor': forms.NumberInput(attrs={'class': 'form-control mt-1 block w-full rounded-md border-black-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'deskripsi_kondisi': forms.Textarea(attrs={'rows': 10, 'class': 'form-control mt-1 block w-full rounded-md border-black-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'kategori_kondisi': forms.Select(attrs={'class': 'form-control mt-1 block w-full rounded-md border-black-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'komentar': forms.Textarea(attrs={'rows': 10, 'class': 'form-control mt-1 block w-full rounded-md border-black-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
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