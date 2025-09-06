# ami/utils/excel_parser.py
import re

def parse_kriteria(cell_value):
    """Menganalisis apakah nilai sel adalah kriteria"""
    if not isinstance(cell_value, str):
        return None
    
    # Pola umum: "Kriteria 1 - Visi, Misi, Tujuan dan Strategi"
    pattern = r'Kriteria\s*(\d+\.?\d*)\s*[-:]?\s*(.*)'
    match = re.search(pattern, cell_value)
    if match:
        kode = match.group(1)
        nama = match.group(2).strip()
        return (kode, nama)
    
    # Cek untuk kriteria dengan nama spesifik
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
    
    for kriteria_nama, kode in kriteria_map.items():
        if kriteria_nama in cell_value:
            return (kode, kriteria_nama)
    
    return None

def parse_elemen(cell_value):
    """Menganalisis apakah nilai sel adalah elemen"""
    if not isinstance(cell_value, str):
        return None
    
    # Pola umum elemen: "1.1 Konsistensi dengan hasil analisis SWOT"
    pattern = r'(\d+\.\d+)\s+(.*)'
    match = re.search(pattern, cell_value)
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
    
    for elemen_nama, kode in elemen_map.items():
        if elemen_nama in cell_value:
            return (kode, elemen_nama)
    
    return None

def parse_indikator(cell_value):
    """Menganalisis apakah nilai sel adalah indikator penilaian"""
    if not isinstance(cell_value, str):
        return None
    
    # Cari pola seperti "Tabel 5.a LKPS" atau "INDIKATOR PENILAIAN"
    if "Tabel" in cell_value or "INDIKATOR PENILAIAN" in cell_value:
        return None
    
    # Cari pola indikator dengan kode
    pattern = r'([A-Z]\d+\.?\d*)\s*[-:]?\s*(.*)'
    match = re.search(pattern, cell_value)
    if match:
        kode = match.group(1)
        deskripsi = match.group(2).strip()
        return (kode, deskripsi)
    
    # Cari indikator tanpa kode eksplisit
    if len(cell_value) > 50:  # Indikator biasanya panjang
        # Cek apakah ini benar-benar indikator dan bukan deskripsi skor
        if not any(prefix in cell_value for prefix in ["Skor", "Jika", "Faktor", "Keterangan"]):
            return ("I" + str(hash(cell_value) % 1000), cell_value)
    
    return None

def parse_skor(cell_value):
    """Menganalisis apakah nilai sel adalah deskripsi skor"""
    if not isinstance(cell_value, str):
        return None
    
    # Pola umum: "Skor 0 = Deskripsi..." atau "Skor 0\nDeskripsi..."
    pattern = r'Skor\s*(\d+)\s*[=:]\s*(.*)'
    match = re.search(pattern, cell_value)
    if match:
        skor = float(match.group(1))
        deskripsi = match.group(2).strip()
        return (skor, deskripsi)
    
    # Pola alternatif: "Skor 0\nDeskripsi..."
    pattern_alt = r'Skor\s*(\d+)\s*\n(.*)'
    match_alt = re.search(pattern_alt, cell_value)
    if match_alt:
        skor = float(match_alt.group(1))
        deskripsi = match_alt.group(2).strip()
        return (skor, deskripsi)
    
    return None

def parse_rumus(cell_value):
    """Menganalisis apakah nilai sel adalah rumus perhitungan"""
    if not isinstance(cell_value, str):
        return None
    
    # Pola umum rumus: "Skor = (A + B) / 2"
    pattern = r'Skor\s*=\s*(.*)'
    match = re.search(pattern, cell_value)
    if match:
        return match.group(1).strip()
    
    return None