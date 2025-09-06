# Dokumentasi Sistem Informasi Audit Mutu Internal (AMI) Universitas Tadulako

## 1. Gambaran Umum

Sistem Informasi Audit Mutu Internal (AMI) adalah aplikasi web yang dirancang khusus untuk mengelola proses audit mutu internal di Universitas Tadulako. Sistem ini membantu universitas dalam memastikan standar mutu pendidikan yang konsisten di seluruh program studi melalui proses audit yang terstruktur dan terdokumentasi.

Sistem ini dibangun dengan teknologi berikut:
- **Framework Backend**: Django 5.2
- **Tampilan**: Tailwind CSS dengan Font Awesome untuk ikon
- **Bahasa Pemrograman**: Python 3.x
- **Sistem Autentikasi**: Django Allauth

## 2. Fitur Utama

### 2.1. Manajemen Data Master
- **Lembaga Akreditasi**: Mengelola lembaga akreditasi yang terkait dengan program studi
- **Program Studi**: Mengelola data program studi beserta akreditasinya
- **Auditor**: Mengelola data auditor internal universitas

### 2.2. Manajemen Proses Audit
- **Sesi Audit**: Mengatur jadwal dan penugasan auditor untuk setiap sesi audit
- **Penilaian Diri**: Memungkinkan program studi melakukan penilaian terhadap diri sendiri
- **Dokumen Pendukung**: Mengunggah bukti pendukung untuk penilaian diri
- **Hasil Audit**: Mencatat hasil audit oleh auditor terhadap penilaian diri
- **Rekomendasi Tindak Lanjut**: Membuat rekomendasi perbaikan berdasarkan hasil audit

### 2.3. Pelaporan
- **Dashboard**: Menampilkan statistik dan aktivitas terkini
- **Laporan Audit**: Menghasilkan laporan komprehensif untuk setiap sesi audit
- **Statistik**: Menampilkan analisis data berdasarkan kriteria dan indikator

## 3. Arsitektur Sistem

### 3.1. Struktur Direktori
```
ami/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── urls.py
├── views.py
└── templates/
    └── ami/
        ├── base.html
        ├── dashboard.html
        ├── lembaga_akreditasi_list.html
        ├── lembaga_akreditasi_form.html
        ├── lembaga_akreditasi_confirm_delete.html
        ├── program_studi_list.html
        ├── program_studi_form.html
        ├── program_studi_detail.html
        ├── program_studi_confirm_delete.html
        ├── auditor_list.html
        ├── auditor_form.html
        ├── audit_session_list.html
        ├── audit_session_form.html
        ├── audit_session_detail.html
        ├── audit_session_confirm_delete.html
        ├── penilaian_diri_list.html
        ├── penilaian_diri_form.html
        ├── audit_list.html
        ├── audit_form.html
        ├── rekomendasi_tindak_lanjut_list.html
        ├── rekomendasi_tindak_lanjut_form.html
        ├── dokumen_pendukung_form.html
        └── laporan_audit.html
```

### 3.2. Model Data

#### 3.2.1. LembagaAkreditasi
- `kode` (CharField): Kode lembaga akreditasi
- `nama` (CharField): Nama lengkap lembaga
- `deskripsi` (TextField): Deskripsi lembaga
- `website` (URLField): Situs web lembaga
- `kontak` (TextField): Informasi kontak

#### 3.2.2. ProgramStudi
- `lembaga_akreditasi` (ForeignKey): Lembaga akreditasi yang mengakreditasi
- `kode` (CharField): Kode program studi
- `nama` (CharField): Nama program studi
- `fakultas` (CharField): Fakultas yang menaungi
- `jenjang` (CharField): Jenjang pendidikan (S1, S2, S3)
- `akreditasi` (CharField): Nilai akreditasi
- `tanggal_akreditasi` (DateField): Tanggal berdiri program studi

#### 3.2.3. Auditor
- `user` (OneToOneField): User Django terkait
- `nip` (CharField): Nomor Induk Pegawai
- `nama_lengkap` (CharField): Nama lengkap auditor
- `jabatan` (CharField): Jabatan dalam universitas
- `unit_kerja` (CharField): Unit kerja auditor
- `nomor_registrasi` (CharField): Nomor registrasi auditor
- `is_auditor_ketua` (BooleanField): Status sebagai auditor ketua

#### 3.2.4. AuditSession
- `program_studi` (ForeignKey): Program studi yang diaudit
- `tahun_akademik` (CharField): Tahun akademik (contoh: 2023/2024)
- `semester` (CharField): Semester (1 atau 2)
- `tanggal_mulai_penilaian_mandiri` (DateField): Tanggal mulai audit
- `tanggal_selesai` (DateField): Tanggal selesai audit
- `status` (CharField): Status sesi audit (diusulkan, berlangsung, selesai)
- `auditor_ketua` (ForeignKey): Auditor ketua
- `auditor_anggota` (ManyToManyField): Auditor anggota

#### 3.2.5. PenilaianDiri
- `audit_session` (ForeignKey): Sesi audit terkait
- `indikator` (ForeignKey): Indikator yang dinilai
- `skor` (DecimalField): Skor penilaian (0-4)
- `komentar` (TextField): Komentar penjelasan
- `status` (CharField): Status penilaian (draf, proses, selesai)
- `tanggal_penilaian` (DateTimeField): Tanggal penilaian dibuat

#### 3.2.6. Audit
- `penilaian_diri` (OneToOneField): Penilaian diri yang diaudit
- `auditor` (ForeignKey): Auditor yang melakukan audit
- `skor` (DecimalField): Skor hasil audit
- `deskripsi_kondisi` (TextField): Deskripsi kondisi hasil audit
- `kategori_kondisi` (CharField): Kategori kondisi (sangat baik, baik, cukup, kurang)
- `komentar` (TextField): Komentar auditor

#### 3.2.7. DokumenPendukung
- `penilaian_diri` (ForeignKey): Penilaian diri terkait
- `nama` (CharField): Nama dokumen
- `file` (FileField): File dokumen
- `deskripsi` (TextField): Deskripsi dokumen

#### 3.2.8. RekomendasiTindakLanjut
- `audit` (OneToOneField): Hasil audit terkait
- `deskripsi` (TextField): Deskripsi rekomendasi
- `prioritas` (CharField): Prioritas (tinggi, sedang, rendah)
- `tenggat_waktu` (DateField): Tenggat waktu penyelesaian
- `status` (CharField): Status (belum dimulai, proses, selesai)
- `bukti_tindak_lanjut` (FileField): Bukti penyelesaian

## 4. Alur Kerja Sistem

### 4.1. Alur Utama Sistem AMI

1. **Persiapan Audit**
   - Admin menambahkan/mengelola data lembaga akreditasi
   - Admin menambahkan/mengelola data program studi
   - Admin menambahkan/mengelola data auditor
   - Admin membuat sesi audit dengan menentukan program studi, periode, dan auditor

2. **Proses Penilaian Diri**
   - Program studi melakukan penilaian diri terhadap indikator yang ditentukan
   - Program studi dapat mengunggah dokumen pendukung untuk setiap penilaian
   - Program studi dapat menyimpan sebagai draft atau menyelesaikan penilaian

3. **Proses Audit**
   - Auditor melakukan audit terhadap penilaian diri yang telah diselesaikan
   - Auditor memberikan skor, deskripsi kondisi, dan kategori kondisi
   - Auditor memberikan komentar terkait penilaian

4. **Rekomendasi dan Tindak Lanjut**
   - Auditor memberikan rekomendasi tindak lanjut berdasarkan hasil audit
   - Program studi menindaklanjuti rekomendasi dan mengunggah bukti
   - Program studi memperbarui status tindak lanjut

5. **Pelaporan**
   - Sistem menghasilkan laporan audit yang komprehensif
   - Laporan mencakup ringkasan eksekutif, skor per kriteria, dan detail indikator
   - Laporan dapat diunduh dan dicetak

### 4.2. Diagram Alur Proses Audit

```
+----------------+      +------------------+      +----------------+      +----------------+
|                |      |                  |      |                |      |                |
|  Persiapan     | ---> |  Penilaian Diri  | ---> |    Audit       | ---> | Rekomendasi &   |
|  Audit         |      |                  |      |                |      | Tindak Lanjut  |
|                |      |                  |      |                |      |                |
+----------------+      +------------------+      +----------------+      +----------------+
        |                                                               |
        v                                                               v
+----------------+                                              +----------------+
|                |                                              |                |
|  Pelaporan     | <------------------------------------------- |  Evaluasi      |
|                |                                              |                |
+----------------+                                              +----------------+
```

## 5. Panduan Penggunaan

### 5.1. Role Pengguna

Sistem AMI memiliki tiga role utama:

1. **Admin**
   - Mengelola data master (lembaga akreditasi, program studi, auditor)
   - Mengelola sesi audit
   - Melihat semua laporan

2. **Program Studi**
   - Melakukan penilaian diri
   - Mengunggah dokumen pendukung
   - Menindaklanjuti rekomendasi
   - Melihat laporan untuk program studi mereka

3. **Auditor**
   - Melakukan audit terhadap penilaian diri
   - Memberikan rekomendasi tindak lanjut
   - Melihat laporan untuk sesi audit yang mereka tangani

### 5.2. Panduan untuk Admin

#### 5.2.1. Mengelola Lembaga Akreditasi
1. Buka menu "Master Data" > "Lembaga Akreditasi"
2. Klik tombol "Tambah Lembaga" untuk menambahkan lembaga baru
3. Isi formulir dengan informasi lembaga
4. Klik "Simpan" untuk menyimpan data

#### 5.2.2. Mengelola Program Studi
1. Buka menu "Master Data" > "Program Studi"
2. Klik tombol "Tambah Program Studi"
3. Isi formulir dengan informasi program studi
4. Klik "Simpan" untuk menyimpan data

#### 5.2.3. Mengelola Auditor
1. Buka menu "Master Data" > "Auditor"
2. Klik tombol "Tambah Auditor"
3. Pilih user yang akan dijadikan auditor
4. Lengkapi informasi auditor
5. Klik "Simpan" untuk menyimpan data

#### 5.2.4. Mengelola Sesi Audit
1. Buka menu "Audit Management" > "Sesi Audit"
2. Klik tombol "Tambah Sesi Audit"
3. Pilih program studi, periode, dan auditor
4. Atur tanggal mulai dan selesai
5. Klik "Simpan" untuk membuat sesi audit

### 5.3. Panduan untuk Program Studi

#### 5.3.1. Melakukan Penilaian Diri
1. Buka menu "Audit Management" > "Sesi Audit"
2. Pilih sesi audit yang aktif untuk program studi Anda
3. Klik tab "Penilaian Diri"
4. Klik "Tambah Penilaian" untuk menilai indikator
5. Isi skor dan komentar untuk setiap indikator
6. (Opsional) Unggah dokumen pendukung
7. Klik "Simpan" untuk menyimpan penilaian

#### 5.3.2. Menindaklanjuti Rekomendasi
1. Buka menu "Audit Management" > "Sesi Audit"
2. Pilih sesi audit yang relevan
3. Klik tab "Rekomendasi"
4. Pilih rekomendasi yang perlu ditindaklanjuti
5. Klik "Edit" untuk memperbarui status
6. Unggah bukti tindak lanjut jika diperlukan
7. Klik "Simpan" untuk memperbarui status

### 5.4. Panduan untuk Auditor

#### 5.4.1. Melakukan Audit
1. Buka menu "Audit Management" > "Sesi Audit"
2. Pilih sesi audit yang ditugaskan kepada Anda
3. Klik tab "Hasil Audit"
4. Pilih penilaian diri yang perlu diaudit
5. Berikan skor, deskripsi kondisi, dan kategori kondisi
6. Tambahkan komentar jika diperlukan
7. Klik "Simpan" untuk menyimpan hasil audit

#### 5.4.2. Memberikan Rekomendasi
1. Buka menu "Audit Management" > "Sesi Audit"
2. Pilih sesi audit yang ditugaskan kepada Anda
3. Klik tab "Rekomendasi"
4. Klik "Tambah Rekomendasi" untuk membuat rekomendasi baru
5. Isi deskripsi rekomendasi dan tentukan prioritas
6. Tetapkan tenggat waktu
7. Klik "Simpan" untuk menyimpan rekomendasi

#### 5.4.3. Melihat Laporan
1. Buka menu "Audit Management" > "Sesi Audit"
2. Pilih sesi audit yang ditugaskan kepada Anda
3. Klik tab "Laporan"
4. Klik "Unduh Laporan" untuk melihat/mencetak laporan audit

## 6. Antarmuka Pengguna

### 6.1. Dashboard
Dashboard merupakan halaman utama sistem yang menampilkan:
- Statistik penting (total program studi, auditor aktif, sesi audit, laporan selesai)
- Aksi cepat untuk memulai proses audit
- Aktivitas terbaru dalam sistem
- Tabel sesi audit terbaru dengan status dan aksi

### 6.2. Navigasi
Sistem menggunakan sidebar navigasi yang responsif dengan struktur berikut:
- **Master Data**: Untuk mengelola data dasar sistem
- **Audit Management**: Untuk mengelola proses audit
- **Laporan**: Untuk melihat dan mengunduh laporan

### 6.3. Responsif
Antarmuka sistem dirancang responsif untuk berbagai ukuran layar:
- Desktop: Sidebar tetap terbuka di sisi kiri
- Mobile: Sidebar disembunyikan dan dapat dibuka dengan tombol hamburger
- Tabel memiliki overflow-x sehingga dapat di-scroll horizontal di layar kecil

## 7. Fitur Keamanan

Sistem AMI memiliki fitur keamanan berikut:
- **Autentikasi**: Menggunakan sistem autentikasi Django
- **Otorisasi**: Setiap pengguna hanya dapat mengakses data yang relevan dengan role-nya
- **Validasi Input**: Formulir memiliki validasi untuk memastikan data yang benar
- **Proteksi CSRF**: Menggunakan token CSRF untuk mencegah serangan CSRF
- **Sanitasi Data**: Data yang ditampilkan di template disanitasi untuk mencegah XSS

## 8. Panduan Pengembangan

### 8.1. Menambahkan Fitur Baru

Untuk menambahkan fitur baru ke sistem AMI, ikuti langkah-langkah berikut:

1. **Buat Model (jika diperlukan)**
   - Tambahkan model baru di `models.py`
   - Buat dan jalankan migrasi dengan `python manage.py makemigrations` dan `python manage.py migrate`

2. **Buat Form**
   - Tambahkan form baru di `forms.py`
   - Sesuaikan fields dan widget sesuai kebutuhan

3. **Buat View**
   - Tambahkan view baru di `views.py`
   - Pastikan implementasi otorisasi yang sesuai
   - Gunakan decorator `@login_required` untuk melindungi view

4. **Buat Template**
   - Buat template HTML baru di `templates/ami/`
   - Pastikan template meng-extend `base.html`
   - Implementasikan responsivitas untuk berbagai ukuran layar

5. **Tambahkan URL**
   - Tambahkan pola URL baru di `urls.py`
   - Pastikan nama URL sesuai dengan konvensi yang ada

### 8.2. Konvensi Penamaan

Sistem AMI menggunakan konvensi penamaan berikut:
- **URL Patterns**: `app_name:view_name` (contoh: `ami:dashboard`)
- **Template**: `nama_view.html` (contoh: `dashboard.html`)
- **View Functions**: `snake_case` (contoh: `audit_session_list`)
- **Model**: `PascalCase` (contoh: `AuditSession`)

## 9. Kesimpulan

Sistem Informasi Audit Mutu Internal (AMI) Universitas Tadulako merupakan solusi terintegrasi untuk mengelola proses audit mutu internal secara efektif dan efisien. Dengan antarmuka yang intuitif dan alur kerja yang terstruktur, sistem ini memudahkan universitas dalam memastikan standar mutu pendidikan yang konsisten di seluruh program studi.

Sistem ini dirancang untuk dapat dikembangkan lebih lanjut sesuai dengan kebutuhan universitas, dengan arsitektur yang modular dan dokumentasi yang lengkap untuk memudahkan proses pengembangan dan pemeliharaan.

Dokumen ini dapat digunakan sebagai panduan untuk penggunaan, pengembangan, dan pemeliharaan sistem AMI Universitas Tadulako.