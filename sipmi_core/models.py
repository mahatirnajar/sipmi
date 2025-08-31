from django.db import models
from django.contrib.auth.models import User # Using default User for simplicity, consider custom user for roles

# Consider creating a custom User model if roles are complex or need extra fields
# class User(AbstractUser):
#     ROLE_CHOICES = (
#         ('admin', 'Admin'),
#         ('auditor', 'Auditor'),
#         ('auditee', 'Auditee (Prodi)'),
#         ('pimpinan', 'Pimpinan'),
#     )
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class ProgramStudi(models.Model):
    nama = models.CharField(max_length=100)
    # Add other relevant fields like Fakultas, Kaprodi (link to User?), etc.

    def __str__(self):
        return self.nama

class Standar(models.Model):
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField()

    def __str__(self):
        return self.nama

class KriteriaED(models.Model):
    standar = models.ForeignKey(Standar, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)
    bobot = models.DecimalField(max_digits=5, decimal_places=2) # e.g., 25.00 for 25%
    STATUS_CHOICES = (
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')

    def __str__(self):
        return f"{self.standar.nama} - {self.nama}"

class JadwalED(models.Model):
    program_studi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE)
    periode = models.CharField(max_length=20) # e.g., "2024/2025"
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    STATUS_CHOICES = (
        ('belum_mulai', 'Belum Mulai'),
        ('berlangsung', 'Berlangsung'),
        ('selesai', 'Selesai'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"ED {self.program_studi} ({self.periode})"

class Auditor(models.Model):
    # Link to Django's User model or a custom one
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nip = models.CharField(max_length=50, blank=True, null=True)
    jabatan = models.CharField(max_length=100, blank=True, null=True)
    SERTIFIKAT_CHOICES = (
        ('ada', 'Ada'),
        ('tidak_ada', 'Tidak Ada'),
    )
    sertifikat_status = models.CharField(max_length=20, choices=SERTIFIKAT_CHOICES, default='tidak_ada')
    STATUS_CHOICES = (
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

class JadwalAMI(models.Model):
    program_studi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE)
    auditor = models.ForeignKey(Auditor, on_delete=models.CASCADE)
    tanggal = models.DateField()
    STATUS_CHOICES = (
        ('terjadwal', 'Terjadwal'),
        ('berlangsung', 'Berlangsung'),
        ('selesai', 'Selesai'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='terjadwal')

    def __str__(self):
        return f"AMI {self.program_studi} oleh {self.auditor} ({self.tanggal})"

class PenugasanAuditor(models.Model):
    auditor = models.ForeignKey(Auditor, on_delete=models.CASCADE)
    program_studi = models.ForeignKey(ProgramStudi, on_delete=models.CASCADE)
    periode = models.CharField(max_length=20) # e.g., "2024/2025"
    STATUS_CHOICES = (
        ('aktif', 'Aktif'),
        ('selesai', 'Selesai'),
        ('ditunda', 'Ditunda'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')

    def __str__(self):
        return f"{self.auditor} -> {self.program_studi} ({self.periode})"

# Consider adding models for:
# - Progress tracking (ED/AMI) - could be complex, involving forms/checklists
# - Actual ED/AMI reports or findings
# - Notifications