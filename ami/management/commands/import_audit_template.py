# ami/management/commands/import_audit_template.py
import os
import re
import openpyxl
from django.core.management.base import BaseCommand
from django.db import transaction
from ami.models import (
    LembagaAkreditasi,
    Kriteria,
    Elemen,
    IndikatorPenilaian,
    SkorIndikator
)

class Command(BaseCommand):
    help = 'Mengimpor template audit dari file Excel ke database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path ke file Excel template')
        parser.add_argument('--lembaga', type=str, help='Nama lembaga akreditasi (misal: LAM InfoKom)', required=True)

    def handle(self, *args, **options):
        file_path = options['file_path']
        lembaga_nama = options['lembaga']
        
        # Pastikan file ada
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File tidak ditemukan: {file_path}'))
            return
        
        # Pastikan lembaga akreditasi ada
        try:
            lembaga = LembagaAkreditasi.objects.get(nama=lembaga_nama)
            self.stdout.write(self.style.SUCCESS(f'Menggunakan lembaga akreditasi: {lembaga.nama}'))
        except LembagaAkreditasi.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Lembaga akreditasi "{lembaga_nama}" tidak ditemukan. Silakan buat terlebih dahulu di admin.'))
            return
        
        # Buka workbook Excel
        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            sheet = workbook.active
            self.stdout.write(self.style.SUCCESS(f'Membuka file: {file_path}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Gagal membuka file Excel: {str(e)}'))
            return
        
        # Ekstrak data dari Excel
        self.stdout.write(self.style.NOTICE('Memulai proses ekstraksi data...'))
        
        try:
            with transaction.atomic():
                self._process_excel_data(sheet, lembaga)
            self.stdout.write(self.style.SUCCESS('Proses impor berhasil diselesaikan!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error selama proses impor: {str(e)}'))
            raise  # Akan rollback transaksi karena ada dalam blok transaction.atomic()

    def _process_excel_data(self, sheet, lembaga):
        """Memproses seluruh data dari sheet Excel"""
        current_kriteria = None
        current_elemen = None
        indikator_data = None
        skor_deskripsi = []
        rumus_perhitungan = None
        memiliki_perhitungan_khusus = False
        row_count = 0
        
        for row in sheet.iter_rows():
            row_count += 1
            values = [cell.value for cell in row if cell.value is not None]
            
            if not values:
                continue
            
            # Cari kriteria
            kriteria_match = self._find_kriteria(values)
            if kriteria_match:
                kriteria_kode, kriteria_nama = kriteria_match
                current_kriteria, created = Kriteria.objects.get_or_create(
                    lembaga_akreditasi=lembaga,
                    kode=kriteria_kode,
                    defaults={'nama': kriteria_nama}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✅ Kriteria baru: {kriteria_kode} - {kriteria_nama}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'ℹ️ Kriteria ada: {kriteria_kode} - {kriteria_nama}'))
                current_elemen = None
                continue
            
            # Cari elemen
            elemen_match = self._find_elemen(values)
            if elemen_match and current_kriteria:
                elemen_kode, elemen_nama = elemen_match
                current_elemen, created = Elemen.objects.get_or_create(
                    kriteria=current_kriteria,
                    kode=elemen_kode,
                    defaults={'nama': elemen_nama}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'   ✅ Elemen baru: {elemen_kode} - {elemen_nama}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'   ℹ️ Elemen ada: {elemen_kode} - {elemen_nama}'))
                continue
            
            # Cari indikator
            indikator_match = self._find_indikator(values)
            if indikator_match and current_elemen:
                # Jika ada indikator sebelumnya yang sedang diproses, simpan dulu
                if indikator_data:
                    self._save_indikator(
                        indikator_data, 
                        current_elemen, 
                        skor_deskripsi, 
                        rumus_perhitungan,
                        memiliki_perhitungan_khusus
                    )
                
                # Reset untuk indikator baru
                indikator_kode, indikator_deskripsi = indikator_match
                indikator_data = {
                    'kode': indikator_kode,
                    'deskripsi': indikator_deskripsi
                }
                skor_deskripsi = []
                rumus_perhitungan = None
                memiliki_perhitungan_khusus = False
                continue
            
            # Cari deskripsi skor
            skor_match = self._find_skor(values)
            if skor_match and indikator_data:
                skor, deskripsi = skor_match
                skor_deskripsi.append((skor, deskripsi))
                continue
            
            # Cari rumus perhitungan
            rumus_match = self._find_rumus(values)
            if rumus_match and indikator_data:
                rumus_perhitungan = rumus_match
                memiliki_perhitungan_khusus = True
                continue
        
        # Simpan indikator terakhir jika ada
        if indikator_data:
            self._save_indikator(
                indikator_data, 
                current_elemen, 
                skor_deskripsi, 
                rumus_perhitungan,
                memiliki_perhitungan_khusus
            )
        
        self.stdout.write(self.style.SUCCESS(f'\nProses selesai! Telah memproses {row_count} baris.'))

    def _find_kriteria(self, values):
        """Mencari pola kriteria dalam baris"""
        # Pola umum: "Kriteria 1 - Visi, Misi, Tujuan dan Strategi"
        for value in values:
            if not isinstance(value, str):
                continue
            
            # Cari pola seperti "Kriteria 1", "Kriteria 1 -", dll.
            pattern = r'Kriteria\s*(\d+\.?\d*)\s*[-:]?\s*(.*)'
            match = re.search(pattern, value)
            if match:
                kode = match.group(1)
                nama = match.group(2).strip()
                return (kode, nama)
        
        # Cek untuk kriteria dengan nama spesifik seperti di file Anda
        kriteria_map = {
            "Kondisi Eksternal": "Kondisi Eksternal",
            "Kriteria 1 - Visi, Misi,Tujuan dan Strategi": "1",
            "Kriteria 2 - Tata Kelola, Tata Pamong, dan Kerjasama": "2",
            "Kriteria 3 - Mahasiswa": "3",
            "Kriteria 4 - Sumber Daya Manusia": "4",
            "Kriteria 5 - Keuangan,Sarana danPrasarana": "5",
            "Kriteria 6 - Pendidikan": "6",
            "Kriteria 7 - Penelitian": "7",
            "Kriteria 8 - Pengabdian kepada Masyarakat": "8",
            "Analisis dan Penetapan Program Pengembangan": "Analisis dan Penetapan Program Pengembangan"
        }
        
        for value in values:
            if not isinstance(value, str):
                continue
            
            for kriteria_nama, kode in kriteria_map.items():
                if kriteria_nama in value:
                    return (kode, kriteria_nama)
        
        return None

    def _find_elemen(self, values):
        """Mencari pola elemen dalam baris"""
        for value in values:
            if not isinstance(value, str):
                continue
            
            # Pola umum elemen: "1.1 Konsistensi dengan hasil analisis SWOT"
            pattern = r'(\d+\.\d+)\s+(.*)'
            match = re.search(pattern, value)
            if match:
                kode = match.group(1)
                nama = match.group(2).strip()
                return (kode, nama)
        
        # Cek elemen spesifik
        elemen_map = {
            "Konsistensi dengan hasil analisis SWOT dan/atau analisis lain serta rencana pengembangan ke depan.": "1.1",
            "Kesesuaian visi, misi, tujuan, dan strategi": "1.2",
            "Kesesuaian kurikulum dengan capaian pembelajaran lulusan": "6.1",
            "Relevansi kurikulum dengan kebutuhan pengguna": "6.2",
            "Rencana pembelajaran tiap mata kuliah": "6.3",
            "Proses pembelajaran": "6.4",
            "Penilaian pembelajaran": "6.5",
            "Integrasi kegiatan penelitian dan PkM dalam pembelajaran": "6.6"
        }
        
        for value in values:
            if not isinstance(value, str):
                continue
            
            for elemen_nama, kode in elemen_map.items():
                if elemen_nama in value:
                    return (kode, elemen_nama)
        
        return None

    def _find_indikator(self, values):
        """Mencari pola indikator penilaian dalam baris"""
        for value in values:
            if not isinstance(value, str):
                continue
            
            # Cari pola seperti "Tabel 5.a LKPS" atau "INDIKATOR PENILAIAN"
            if "Tabel" in value or "INDIKATOR PENILAIAN" in value:
                continue
            
            # Cari pola indikator dengan kode
            pattern = r'([A-Z]\d+\.?\d*)\s*[-:]?\s*(.*)'
            match = re.search(pattern, value)
            if match:
                kode = match.group(1)
                deskripsi = match.group(2).strip()
                return (kode, deskripsi)
            
            # Cari indikator tanpa kode eksplisit
            if len(value) > 50:  # Indikator biasanya panjang
                # Cek apakah ini benar-benar indikator dan bukan deskripsi skor
                if not any(prefix in value for prefix in ["Skor", "Jika", "Faktor", "Keterangan"]):
                    return ("I" + str(hash(value) % 1000), value)
        
        return None

    def _find_skor(self, values):
        """Mencari deskripsi skor (0-4) dalam baris"""
        for value in values:
            if not isinstance(value, str):
                continue
            
            # Pola umum: "Skor 0 = Deskripsi..." atau "Skor 0\nDeskripsi..."
            pattern = r'Skor\s*(\d+)\s*[=:]\s*(.*)'
            match = re.search(pattern, value)
            if match:
                skor = float(match.group(1))
                deskripsi = match.group(2).strip()
                return (skor, deskripsi)
            
            # Pola alternatif: "Skor 0\nDeskripsi..."
            pattern_alt = r'Skor\s*(\d+)\s*\n(.*)'
            match_alt = re.search(pattern_alt, value)
            if match_alt:
                skor = float(match_alt.group(1))
                deskripsi = match_alt.group(2).strip()
                return (skor, deskripsi)
        
        return None

    def _find_rumus(self, values):
        """Mencari rumus perhitungan dalam baris"""
        for value in values:
            if not isinstance(value, str):
                continue
            
            # Pola umum rumus: "Skor = (A + B) / 2"
            pattern = r'Skor\s*=\s*(.*)'
            match = re.search(pattern, value)
            if match:
                return match.group(1).strip()
        
        return None

    def _save_indikator(self, indikator_data, elemen, skor_deskripsi, rumus_perhitungan, memiliki_perhitungan_khusus):
        """Menyimpan indikator dan deskripsi skor ke database"""
        # Cari atau buat indikator
        indikator, created = IndikatorPenilaian.objects.get_or_create(
            elemen=elemen,
            kode=indikator_data['kode'],
            defaults={
                'deskripsi': indikator_data['deskripsi'],
                'panduan': '',
                'skor_maksimal': 4.0,
                'memiliki_perhitungan_khusus': memiliki_perhitungan_khusus,
                'rumus_perhitungan': rumus_perhitungan if memiliki_perhitungan_khusus else None
            }
        )
        
        if created:
            status = "✅"
            msg = f'      Indikator baru: {indikator.kode}'
        else:
            status = "ℹ️"
            msg = f'      Indikator ada: {indikator.kode}'
            # Update jika diperlukan
            if memiliki_perhitungan_khusus and indikator.rumus_perhitungan != rumus_perhitungan:
                indikator.memiliki_perhitungan_khusus = memiliki_perhitungan_khusus
                indikator.rumus_perhitungan = rumus_perhitungan
                indikator.save()
        
        self.stdout.write(f'{status} {msg}')
        
        # Simpan deskripsi skor
        for skor, deskripsi in skor_deskripsi:
            SkorIndikator.objects.get_or_create(
                indikator=indikator,
                skor=skor,
                defaults={'deskripsi': deskripsi}
            )
        
        # Tampilkan ringkasan
        self.stdout.write(f'        • Deskripsi skor: {len(skor_deskripsi)} item')
        if memiliki_perhitungan_khusus and rumus_perhitungan:
            self.stdout.write(f'        • Rumus: {rumus_perhitungan}')