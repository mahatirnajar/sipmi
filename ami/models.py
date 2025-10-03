from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone

# Model untuk kategori kondisi yang digunakan oleh auditor
class KategoriKondisi(models.TextChoices):
    SESUAI = 'SESUAI', _('Sesuai')
    KT_MINOR = 'KT_MINOR', _('Ketidaksesuaian Minor')
    KT_MAYOR = 'KT_MAYOR', _('Ketidaksesuaian Mayor')

class LembagaAkreditasi(models.Model):
    """Model untuk lembaga akreditasi seperti LAM InfoKom, LAM Sains, dll."""
    kode = models.CharField(max_length=20, unique=True)
    nama = models.CharField(max_length=255, unique=True)
    deskripsi = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    kontak = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Lembaga Akreditasi"
        verbose_name_plural = "Lembaga Akreditasi"
        ordering = ['nama']
    
    def __str__(self):
        return self.nama

class Kriteria(models.Model):
    """Model untuk kriteria penilaian (level tertinggi)"""
    lembaga_akreditasi = models.ForeignKey(LembagaAkreditasi, on_delete=models.CASCADE, related_name='kriteria')
    kode = models.CharField(max_length=30, null=True)
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('aktif', 'aktif'),
        ('tidak aktif', 'tidak aktif'),
    ], default='aktif')
    
    
    class Meta:
        verbose_name = "Kriteria"
        verbose_name_plural = "Kriteria"
        unique_together = ['lembaga_akreditasi', 'kode']
        ordering = ['kode']
    
    def __str__(self):
        return f"{self.kode} - {self.nama}"

class Elemen(models.Model):
    """Model untuk elemen penilaian (bagian dari kriteria)"""
    kriteria = models.ForeignKey(Kriteria, on_delete=models.CASCADE, related_name='elemen')
    kode = models.CharField(max_length=30)
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True, null=True)
    panduan = models.TextField(blank=True, null=True)
    skor_maksimal = models.FloatField(default=4.0)
    status = models.CharField(max_length=20, choices=[
        ('aktif', 'aktif'),
        ('tidak aktif', 'tidak aktif'),
    ], default='aktif')
    class Meta:
        verbose_name = "Elemen"
        verbose_name_plural = "Elemen"
        unique_together = ['kriteria', 'kode']
        ordering = ['kode']
    
    def __str__(self):
        return f"{self.kode} - {self.nama}"

class ProgramStudi(models.Model):
    """Model untuk program studi yang diaudit"""
    lembaga_akreditasi = models.ForeignKey(LembagaAkreditasi, on_delete=models.PROTECT, related_name='program_studi')
    kode = models.CharField(max_length=10, unique=True)
    nama = models.CharField(max_length=255)
    fakultas = models.CharField(max_length=200, choices=[
        ('FKIP', 'FKIP'),
        ('FISIP', 'FISIP'),
        ('FEB', 'FEB'),
        ('FAKUM', 'FAKUM'),
        ('FAPERTA', 'FAPERTA'),
        ('FATEK', 'FATEK'),
        ('FMIPA', 'FMIPA'),
        ('FAHUT', 'FAHUT'),
        ('FK', 'FK'),
        ('FAPETKAN', 'FAPETKAN'),
        ('FKM', 'FKM'),
        ('Pascasarjana', 'Pascasarjana'),
        
    ])
    jenjang = models.CharField(max_length=50, choices=[
        ('D3', 'Diploma 3'),
        ('D4', 'Diploma 4'),
        ('S1', 'Sarjana'),
        ('S2', 'Magister'),
        ('S3', 'Doktor'),
        ('Profesi','Profesi')
    ])
    akreditasi = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('unggul', 'UNGGUL'),
        ('baik_sekali', 'BAIK SEKALI'),
        ('baik', 'BAIK'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('belum', 'Belum Terakreditasi')
    ] )
    tanggal_akreditasi = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Program Studi"
        verbose_name_plural = "Program Studi"
        ordering = ['kode']
    
    def __str__(self):
        return f"{self.kode} - {self.nama} ({self.jenjang})"

class KoordinatorProgramStudi(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nuptk = models.CharField(max_length=20, unique=True)
    nama_lengkap = models.CharField(max_length=255)
    program_studi = models.ForeignKey(
        ProgramStudi, 
        null=True,
        on_delete=models.SET_NULL,
        related_name='koordinators'
    )
    
    class Meta:
        verbose_name = "Koordinator Program Studi"
        verbose_name_plural = "Koordinator Program Studi"
        ordering = ['nama_lengkap']
    
    def __str__(self):
        return f"{self.nama_lengkap} ({self.nuptk})"
class Auditor(models.Model):
    """Model untuk auditor"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nuptk = models.CharField(max_length=20, unique=True)
    nama_lengkap = models.CharField(max_length=255)
    jabatan = models.CharField(max_length=255)
    unit_kerja = models.CharField(max_length=255)
    nomor_registrasi = models.CharField(max_length=50, blank=True, null=True)
    is_auditor_ketua = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('aktif', 'aktif'),
        ('tidak aktif', 'tidak aktif'),
    ], default='aktif')
    
    
    class Meta:
        verbose_name = "Auditor"
        verbose_name_plural = "Auditor"
        ordering = ['nama_lengkap']
    
    def __str__(self):
        return f"{self.nama_lengkap} ({self.nuptk})"

class AuditSession(models.Model):
    """Model untuk sesi audit (mengelompokkan penilaian untuk satu siklus audit)"""
    program_studi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE, related_name='audit_sessions')
    tahun_akademik = models.CharField(max_length=9)  # Contoh: "2023/2024"
    semester = models.CharField(max_length=2, choices=[
        ('G', 'Ganjil'),
        ('P', 'Genap'),
    ])
    tanggal_mulai_penilaian_mandiri = models.DateField(blank=True, null=True)
    tanggal_selesai_penilaian_mandiri = models.DateField(blank=True, null=True)
    tanggal_mulai_penilaian_auditor = models.DateField(blank=True, null=True)
    tanggal_selesai_penilaian_auditor = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'Draft'),
        ('PENILAIAN_MANDIRI', 'Penilaian Mandiri'),  # Diperbaiki typo
        ('PENILAIAN_AUDITOR', 'Penilaian Auditor'),  # Diperbaiki typo
        ('SELESAI', 'SELESAI'),
    ], default='DRAFT')
    
    auditor_ketua = models.ForeignKey(Auditor, on_delete=models.SET_NULL, null=True, blank=True, related_name='ketua_audit_sessions')
    auditor_anggota = models.ManyToManyField(Auditor, related_name='anggota_audit_sessions', blank=True)
    
    def update_status(self):
        """Perbarui status berdasarkan tanggal saat ini."""
        today = timezone.now().date()
        # Jika belum ada tanggal mulai mandiri, tetap di DRAFT
        if not self.tanggal_mulai_penilaian_mandiri:
            return
        
        # Draft → Penilaian Mandiri
        if self.status == 'DRAFT' and today >= self.tanggal_mulai_penilaian_mandiri:
            self.status = 'PENILAIAN_MANDIRI'  
            self.save(update_fields=['status'])
            return
        
        # Penilaian Mandiri → Penilaian Auditor
        if self.status == 'PENILAIAN_MANDIRI' and self.tanggal_selesai_penilaian_mandiri:
            if today > self.tanggal_selesai_penilaian_mandiri:
                if self.tanggal_mulai_penilaian_auditor and today >= self.tanggal_mulai_penilaian_auditor:
                    self.status = 'PENILAIAN_AUDITOR'  
                    self.save(update_fields=['status'])
                    return
        
        # Penilaian Auditor → Selesai
        if self.status == 'PENILAIAN_AUDITOR' and self.tanggal_selesai_penilaian_auditor:
            if today > self.tanggal_selesai_penilaian_auditor:
                self.status = 'SELESAI'
                self.save(update_fields=['status'])
                return
            
    class Meta:
        verbose_name = "Sesi Audit"
        verbose_name_plural = "Sesi Audit"
        unique_together = ['program_studi', 'tahun_akademik', 'semester']
        ordering = ['-tanggal_mulai_penilaian_mandiri']
    
    def __str__(self):
        return f"{self.program_studi} - {self.tahun_akademik} {self.semester}"

class PenilaianDiri(models.Model):
    """Model untuk penilaian diri yang dilakukan oleh program studi"""
    audit_session = models.ForeignKey(AuditSession, on_delete=models.CASCADE, related_name='penilaian_diri')
    elemen = models.ForeignKey(Elemen, on_delete=models.CASCADE, null=True)
    skor = models.FloatField(null=True, blank=True)
    bukti_dokumen = models.URLField(blank=True, null=True)  # Sudah menggunakan URLField
    komentar = models.TextField(blank=True, null=True)
    tanggal_penilaian = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('BELUM', 'Belum Dinilai'),
        ('TERISI', 'Sudah Terisi'),
        ('DIAJUKAN', 'Diajukan untuk Audit'),
    ], default='BELUM')
    
    class Meta:
        verbose_name = "Penilaian Diri"
        verbose_name_plural = "Penilaian Diri"
        unique_together = ['audit_session', 'elemen']
        ordering = ['elemen__kode']
    
    def clean(self):
        super().clean()
        if self.skor is not None:
            if self.skor < 0:
                raise ValidationError({'skor': 'Skor tidak boleh kurang dari 0.'})
            if self.elemen and self.skor > self.elemen.skor_maksimal:
                raise ValidationError({
                    'skor': f'Skor tidak boleh melebihi {self.elemen.skor_maksimal} (skor maksimal untuk indikator ini).'
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # memastikan validasi dijalankan sebelum save
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.elemen.kode} - {self.audit_session.program_studi}"

class Audit(models.Model):
    """Model untuk hasil audit yang dilakukan oleh auditor"""
    penilaian_diri = models.OneToOneField(PenilaianDiri, on_delete=models.CASCADE, related_name='audit')
    skor = models.FloatField(null=True, blank=True)
    deskripsi_kondisi = models.TextField(default="Tolong Tuliskan Deskrpisi Penilaian")
    kategori_kondisi = models.CharField(max_length=20, choices=KategoriKondisi.choices, blank=True, null=True)
    komentar = models.TextField(blank=True, null=True)
    tanggal_audit = models.DateTimeField(auto_now_add=True)
    auditor = models.ForeignKey(Auditor, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Audit"
        verbose_name_plural = "Audit"
        ordering = ['penilaian_diri__elemen__kode']
    
    def __str__(self):
        return f"Audit {self.penilaian_diri.elemen.kode} - {self.penilaian_diri.audit_session.program_studi}"

class DokumenPendukung(models.Model):
    """Model untuk dokumen pendukung tambahan"""
    penilaian_diri = models.ForeignKey(PenilaianDiri, on_delete=models.CASCADE, related_name='dokumen_pendukung')
    nama = models.CharField(max_length=255)
    file = models.FileField(upload_to='dokumen_pendukung/')
    deskripsi = models.TextField(blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Dokumen Pendukung"
        verbose_name_plural = "Dokumen Pendukung"
        ordering = ['-tanggal_upload']
    
    def __str__(self):
        return f"{self.nama} - {self.penilaian_diri.elemen.kode}"

class CatatanAudit(models.Model):
    """Model untuk catatan atau komentar selama proses audit"""
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='catatan')
    auditor = models.ForeignKey(Auditor, on_delete=models.SET_NULL, null=True, blank=True)
    catatan = models.TextField()
    tanggal_catatan = models.DateTimeField(auto_now_add=True)
    dibalas_ke = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='balasan')
    
    class Meta:
        verbose_name = "Catatan Audit"
        verbose_name_plural = "Catatan Audit"
        ordering = ['tanggal_catatan']
    
    def __str__(self):
        return f"Catatan oleh {self.auditor} pada {self.tanggal_catatan}"

class RekomendasiTindakLanjut(models.Model):
    """Model untuk rekomendasi tindak lanjut dari hasil audit"""
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='rekomendasi')
    deskripsi = models.TextField()
    prioritas = models.CharField(max_length=10, choices=[
        ('TINGGI', 'Tinggi'),
        ('SEDANG', 'Sedang'),
        ('RENDAH', 'Rendah'),
    ], default='SEDANG')
    tenggat_waktu = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('BELUM', 'Belum Ditindaklanjuti'),
        ('SEDANG', 'Sedang Ditindaklanjuti'),
        ('SELESAI', 'Selesai'),
    ], default='BELUM')
    bukti_tindak_lanjut = models.FileField(upload_to='tindak_lanjut/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Rekomendasi Tindak Lanjut"
        verbose_name_plural = "Rekomendasi Tindak Lanjut"
        ordering = ['-tenggat_waktu']
    
    def __str__(self):
        return f"Rekomendasi untuk {self.audit.penilaian_diri.elemen.kode}"