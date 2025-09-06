import pandas as pd
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Import data akreditasi dari file Excel BAN-PT'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')
        parser.add_argument('--lembaga-kode', type=str, default='BANPT', help='Kode lembaga akreditasi')
        parser.add_argument('--lembaga-nama', type=str, default='Badan Akreditasi Nasional Perguruan Tinggi', 
                           help='Nama lembaga akreditasi')

    def clean_text(self, text):
        """Bersihkan teks dari karakter tidak perlu"""
        if not isinstance(text, str) or pd.isna(text):
            return ""
        # Hapus karakter tidak standar
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        # Hapus karakter whitespace berlebih
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_skor_descriptions(self, text):
        """Ekstrak deskripsi skor dari teks"""
        if not text:
            return []
        
        skor_descriptions = []
        # Pola untuk mendeteksi skor dalam berbagai format
        skor_pattern = r'(Skor\s*\d+\.?\d*|\d+\s*=\s*|Skor\s*=\s*\d+\.?\d*)\s*[:=]?\s*(.*?)(?=\s*Skor\s*\d+|$)'
        matches = re.findall(skor_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            skor_text = match[0].replace('Skor', '').replace('=', '').strip()
            try:
                skor = float(skor_text)
                description = match[1].strip()
                if description:
                    skor_descriptions.append((skor, description))
            except ValueError:
                continue
        
        # Jika tidak ada pola skor yang ditemukan, coba pola alternatif
        if not skor_descriptions:
            lines = text.split('\n')
            current_skor = None
            current_desc = []
            
            for line in lines:
                line = self.clean_text(line)
                if not line:
                    continue
                
                # Cek apakah baris dimulai dengan "Skor X"
                if re.match(r'^Skor\s*\d+\.?\d*', line, re.IGNORECASE):
                    if current_skor is not None and current_desc:
                        skor_descriptions.append((current_skor, " ".join(current_desc)))
                        current_desc = []
                    
                    skor_match = re.search(r'Skor\s*(\d+\.?\d*)', line, re.IGNORECASE)
                    if skor_match:
                        current_skor = float(skor_match.group(1))
                        desc_part = re.sub(r'Skor\s*\d+\.?\d*\s*[:=]?\s*', '', line).strip()
                        if desc_part:
                            current_desc.append(desc_part)
                elif current_skor is not None:
                    current_desc.append(line)
            
            # Tambahkan skor terakhir
            if current_skor is not None and current_desc:
                skor_descriptions.append((current_skor, " ".join(current_desc)))
        
        return skor_descriptions

    def handle(self, *args, **options):
        file_path = options['file_path']
        lembaga_kode = 'BANPT' 
        lembaga_nama = 'Badan Akreditasi Nasional Perguruan Tinggi'
        
        # Ambil model-model yang diperlukan
        LembagaAkreditasi = apps.get_model('ami', 'LembagaAkreditasi')
        Kriteria = apps.get_model('ami', 'Kriteria')
        Elemen = apps.get_model('ami', 'Elemen')
        IndikatorPenilaian = apps.get_model('ami', 'IndikatorPenilaian')
        SkorIndikator = apps.get_model('ami', 'SkorIndikator')
        
        # Pastikan Lembaga Akreditasi sudah ada
        lembaga, created = LembagaAkreditasi.objects.get_or_create(
            kode=lembaga_kode,
            defaults={
                'nama': lembaga_nama,
                'deskripsi': 'Lembaga akreditasi untuk perguruan tinggi di Indonesia',
                'website': 'https://banpt.or.id',
                'kontak': 'Jl. Diponegoro No.24, Jakarta'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Lembaga Akreditasi: {lembaga.nama}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing Lembaga Akreditasi: {lembaga.nama}'))
        
        # Baca file Excel
        try:
            # Baca sheet pertama saja
            df = pd.read_excel(file_path, sheet_name='Kertas Kerja', header=None)
            
            # Inisialisasi variabel untuk melacak struktur
            current_kriteria = None
            current_elemen = None
            potential_indicator = None
            collecting_description = False
            indicator_description = ""
            processed_indicators = set()
            
            self.stdout.write(self.style.NOTICE('Starting data import...'))
            
            for index, row in df.iterrows():
                # Gabungkan semua cell dalam baris dan bersihkan
                row_text = " ".join([self.clean_text(str(cell)) for cell in row if self.clean_text(str(cell)) != ''])
                
                if not row_text:
                    continue
                
                # Lewati baris header
                if "PENILAIAN AKREDITASI PROGRAM STUDI" in row_text:
                    continue
                
                # Cari pola tabel yang menunjukkan struktur kriteria (Tabel X.Y atau Tabel X.Y.Z)
                tabel_match = re.search(r'Tabel\s+(\d+)\.([a-zA-Z]+)(?:\.(\d+))?', row_text)
                print(tabel_match)
                if tabel_match:
                    kriteria_num = tabel_match.group(1)
                    elemen_code = tabel_match.group(2).upper()
                    indikator_num = tabel_match.group(3) if tabel_match.group(3) else None
                    print(kriteria_num)
                    print(elemen_code)
                    print(indikator_num)

                    # Buat atau ambil kriteria jika belum ada
                    kriteria_kode = f"K{kriteria_num}"
                    try:
                        kriteria, created = Kriteria.objects.get_or_create(
                            lembaga_akreditasi=lembaga,
                            kode=kriteria_kode,
                            defaults={
                                'nama': f"Kriteria {kriteria_num}",
                                'deskripsi': f"Kriteria {kriteria_num} dari BAN-PT"
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Created Kriteria: {kriteria.kode} - {kriteria.nama}'))
                        current_kriteria = kriteria
                    except IntegrityError:
                        kriteria = Kriteria.objects.get(lembaga_akreditasi=lembaga, kode=kriteria_kode)
                        current_kriteria = kriteria
                        self.stdout.write(self.style.SUCCESS(f'Using Kriteria: {kriteria.kode} - {kriteria.nama}'))
                    
                    # Buat atau ambil elemen jika belum ada
                    elemen_kode = f"{elemen_code}."
                    try:
                        elemen, created = Elemen.objects.get_or_create(
                            kriteria=current_kriteria,
                            kode=elemen_kode,
                            defaults={
                                'nama': f"Elemen {elemen_code}",
                                'deskripsi': f"Elemen {elemen_code} dari Kriteria {kriteria_num}"
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'  Created Elemen: {elemen.kode} - {elemen.nama}'))
                        current_elemen = elemen
                    except IntegrityError:
                        elemen = Elemen.objects.get(kriteria=current_kriteria, kode=elemen_kode)
                        current_elemen = elemen
                        self.stdout.write(self.style.SUCCESS(f'  Using Elemen: {elemen.kode} - {elemen.nama}'))
                    
                    # Reset indikator potensial
                    potential_indicator = None
                    collecting_description = False
                    indicator_description = ""
                
                # Cari teks indikator yang mungkin
                if current_elemen and not collecting_description:
                    # Cari teks yang mungkin merupakan indikator
                    if re.search(r'Skor\s+\d+', row_text) or re.search(r'Skor\s*=\s*\d+', row_text):
                        potential_indicator = row_text
                        collecting_description = True
                        indicator_description = row_text
                    elif not re.search(r'Tabel\s+\d+\.[a-zA-Z]+', row_text) and not re.search(r'%\s+(Sangat Baik|Baik|Cukup|Kurang)', row_text):
                        # Jika baris tidak mengandung pola tabel atau persentase, mungkin merupakan deskripsi indikator
                        potential_indicator = row_text
                
                # Kumpulkan deskripsi indikator
                if current_elemen and collecting_description and potential_indicator:
                    indicator_description += " " + row_text
                    
                    # Jika baris berikutnya tidak mengandung pola skor, lanjutkan mengumpulkan
                    if not re.search(r'Skor\s+\d+', row_text) and not re.search(r'Skor\s*=\s*\d+', row_text):
                        collecting_description = True
                    else:
                        # Selesai mengumpulkan, proses indikator
                        indicator_key = f"{current_elemen.id}_{potential_indicator[:50]}"
                        if indicator_key not in processed_indicators:
                            processed_indicators.add(indicator_key)
                            
                            # Buat kode indikator
                            indikator_count = IndikatorPenilaian.objects.filter(elemen=current_elemen).count() + 1
                            indikator_kode = f"{current_elemen.kode}{indikator_count}"
                            
                            # Buat indikator
                            try:
                                with transaction.atomic():
                                    indikator = IndikatorPenilaian.objects.create(
                                        elemen=current_elemen,
                                        kode=indikator_kode,
                                        deskripsi=indicator_description,
                                        skor_maksimal=4.0
                                    )
                                    
                                    # Ekstrak dan simpan deskripsi skor
                                    skor_descriptions = self.extract_skor_descriptions(indicator_description)
                                    for skor, description in skor_descriptions:
                                        SkorIndikator.objects.create(
                                            indikator=indikator,
                                            skor=skor,
                                            deskripsi=description
                                        )
                                    
                                    self.stdout.write(self.style.SUCCESS(f'    Created Indikator: {indikator.kode}'))
                                    self.stdout.write(self.style.SUCCESS(f'      Found {len(skor_descriptions)} score descriptions'))
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'    Error creating Indikator: {str(e)}'))
                        
                        # Reset untuk indikator berikutnya
                        potential_indicator = None
                        collecting_description = False
                        indicator_description = ""
            
            # Cari indikator yang mungkin terlewat
            if current_elemen and potential_indicator and not collecting_description:
                indicator_key = f"{current_elemen.id}_{potential_indicator[:50]}"
                if indicator_key not in processed_indicators:
                    processed_indicators.add(indicator_key)
                    
                    indikator_count = IndikatorPenilaian.objects.filter(elemen=current_elemen).count() + 1
                    indikator_kode = f"{current_elemen.kode}{indikator_count}"
                    
                    try:
                        with transaction.atomic():
                            indikator = IndikatorPenilaian.objects.create(
                                elemen=current_elemen,
                                kode=indikator_kode,
                                deskripsi=potential_indicator,
                                skor_maksimal=4.0
                            )
                            
                            skor_descriptions = self.extract_skor_descriptions(potential_indicator)
                            for skor, description in skor_descriptions:
                                SkorIndikator.objects.create(
                                    indikator=indikator,
                                    skor=skor,
                                    deskripsi=description
                                )
                            
                            self.stdout.write(self.style.SUCCESS(f'    Created final Indikator: {indikator.kode}'))
                            self.stdout.write(self.style.SUCCESS(f'      Found {len(skor_descriptions)} score descriptions'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'    Error creating final Indikator: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS('Data import completed successfully'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing Excel file: {str(e)}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))