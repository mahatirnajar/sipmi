# ami/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden, Http404
from django.core.paginator import Paginator
from .models import (
    LembagaAkreditasi,
    ProgramStudi,
    Auditor,
    AuditSession,
    PenilaianDiri,
    Audit,
    DokumenPendukung,
    RekomendasiTindakLanjut
)
from .forms import (
    LembagaAkreditasiForm,
    ProgramStudiForm,
    AuditorForm,
    AuditSessionForm,
    PenilaianDiriForm,
    AuditForm,
    DokumenPendukungForm,
    RekomendasiTindakLanjutForm
)

# ----------------------------
# Helper Functions
# ----------------------------
def get_user_program_studi(user):
    """Mendapatkan program studi yang terkait dengan user"""
    try:
        return user.programstudi
    except:
        return None

def get_user_auditor(user):
    """Mendapatkan objek auditor yang terkait dengan user"""
    try:
        return user.auditor
    except:
        return None

def check_program_studi_permission(user, program_studi):
    """Memeriksa apakah user memiliki izin untuk mengakses program studi tertentu"""
    user_program_studi = get_user_program_studi(user)
    return user_program_studi == program_studi

def check_audit_session_permission(user, audit_session):
    """Memeriksa apakah user memiliki izin untuk mengakses sesi audit tertentu"""
    # Pemeriksaan untuk program studi
    if get_user_program_studi(user) == audit_session.program_studi:
        return True
    
    # Pemeriksaan untuk auditor
    user_auditor = get_user_auditor(user)
    if user_auditor:
        return (user_auditor == audit_session.auditor_ketua or 
                user_auditor in audit_session.auditor_anggota.all())
    
    return False

# ----------------------------
# Dashboard Views
# ----------------------------
@login_required
def dashboard(request):
    """View untuk halaman dashboard"""
    # Hitung statistik untuk dashboard
    total_program_studi = ProgramStudi.objects.count()
    total_audit_session = AuditSession.objects.count()
    total_penilaian_diri = PenilaianDiri.objects.count()
    total_audit = Audit.objects.count()
    
    # Ambil beberapa data terbaru
    latest_audit_sessions = AuditSession.objects.select_related('program_studi').order_by('-tanggal_mulai')[:5]
    latest_penilaian_diri = PenilaianDiri.objects.select_related(
        'audit_session', 'audit_session__program_studi', 'indikator'
    ).order_by('-tanggal_penilaian')[:5]
    
    # Data untuk grafik
    kriteria_data = []
    if latest_audit_sessions:
        # Ambil sesi audit terbaru untuk data grafik
        latest_session = latest_audit_sessions[0]
        kriteria_list = latest_session.program_studi.lembaga_akreditasi.kriteria.all()
        
        for kriteria in kriteria_list:
            # Hitung rata-rata skor untuk kriteria ini
            total_skor = 0
            count = 0
            
            for elemen in kriteria.elemen.all():
                for indikator in elemen.indikator.all():
                    try:
                        penilaian = PenilaianDiri.objects.get(
                            audit_session=latest_session,
                            indikator=indikator
                        )
                        if penilaian.skor is not None:
                            total_skor += penilaian.skor
                            count += 1
                    except PenilaianDiri.DoesNotExist:
                        pass
            
            if count > 0:
                rata_rata = total_skor / count
                kriteria_data.append({
                    'nama': kriteria.nama,
                    'rata_rata': round(rata_rata, 2)
                })
    
    context = {
        'total_program_studi': total_program_studi,
        'total_audit_session': total_audit_session,
        'total_penilaian_diri': total_penilaian_diri,
        'total_audit': total_audit,
        'latest_audit_sessions': latest_audit_sessions,
        'latest_penilaian_diri': latest_penilaian_diri,
        'kriteria_data': kriteria_data,
    }
    
    return render(request, 'ami/dashboard.html', context)

# ----------------------------
# Views untuk Lembaga Akreditasi
# ----------------------------
@login_required
def lembaga_akreditasi_list(request):
    """View untuk menampilkan daftar lembaga akreditasi"""
    lembaga_akreditasi_list = LembagaAkreditasi.objects.all().order_by('nama')
    
    # Pagination
    paginator = Paginator(lembaga_akreditasi_list, 10)
    page_number = request.GET.get('page')
    lembaga_akreditasi = paginator.get_page(page_number)
    
    return render(request, 'ami/lembaga_akreditasi_list.html', {
        'lembaga_akreditasi': lembaga_akreditasi
    })

@login_required
def lembaga_akreditasi_create(request):
    """View untuk membuat lembaga akreditasi baru"""
    if request.method == 'POST':
        form = LembagaAkreditasiForm(request.POST)
        if form.is_valid():
            lembaga = form.save()
            messages.success(request, f'Lembaga akreditasi "{lembaga.nama}" berhasil dibuat.')
            return redirect('ami:lembaga_akreditasi_list')
    else:
        form = LembagaAkreditasiForm()
    
    return render(request, 'ami/lembaga_akreditasi_form.html', {
        'form': form,
        'title': 'Tambah Lembaga Akreditasi'
    })

@login_required
def lembaga_akreditasi_update(request, pk):
    """View untuk memperbarui lembaga akreditasi"""
    lembaga = get_object_or_404(LembagaAkreditasi, pk=pk)
    
    if request.method == 'POST':
        form = LembagaAkreditasiForm(request.POST, instance=lembaga)
        if form.is_valid():
            lembaga = form.save()
            messages.success(request, f'Lembaga akreditasi "{lembaga.nama}" berhasil diperbarui.')
            return redirect('ami:lembaga_akreditasi_list')
    else:
        form = LembagaAkreditasiForm(instance=lembaga)
    
    return render(request, 'ami/lembaga_akreditasi_form.html', {
        'form': form,
        'title': f'Edit {lembaga.nama}'
    })

@login_required
def lembaga_akreditasi_delete(request, pk):
    """View untuk menghapus lembaga akreditasi"""
    lembaga = get_object_or_404(LembagaAkreditasi, pk=pk)
    
    if request.method == 'POST':
        nama = lembaga.nama
        lembaga.delete()
        messages.success(request, f'Lembaga akreditasi "{nama}" berhasil dihapus.')
        return redirect('ami:lembaga_akreditasi_list')
    
    return render(request, 'ami/lembaga_akreditasi_confirm_delete.html', {
        'lembaga': lembaga
    })

# ----------------------------
# Views untuk Program Studi
# ----------------------------
@login_required
def program_studi_list(request):
    """View untuk menampilkan daftar program studi"""
    program_studi_list = ProgramStudi.objects.select_related('lembaga_akreditasi').all().order_by('kode')
    
    # Pagination
    paginator = Paginator(program_studi_list, 10)
    page_number = request.GET.get('page')
    program_studi = paginator.get_page(page_number)
    
    return render(request, 'ami/program_studi_list.html', {
        'program_studi': program_studi
    })

@login_required
def program_studi_create(request):
    """View untuk membuat program studi baru"""
    if request.method == 'POST':
        form = ProgramStudiForm(request.POST)
        if form.is_valid():
            program = form.save()
            messages.success(request, f'Program studi "{program.nama}" berhasil dibuat.')
            return redirect('ami:program_studi_list')
    else:
        form = ProgramStudiForm()
    
    return render(request, 'ami/program_studi_form.html', {
        'form': form,
        'title': 'Tambah Program Studi'
    })

@login_required
def program_studi_detail(request, pk):
    """View untuk detail program studi"""
    program = get_object_or_404(ProgramStudi, pk=pk)
    audit_sessions = program.audit_sessions.all().order_by('-tanggal_mulai')
    
    context = {
        'program': program,
        'audit_sessions': audit_sessions
    }
    
    return render(request, 'ami/program_studi_detail.html', context)

@login_required
def program_studi_update(request, pk):
    """View untuk memperbarui program studi"""
    program = get_object_or_404(ProgramStudi, pk=pk)
    
    if request.method == 'POST':
        form = ProgramStudiForm(request.POST, instance=program)
        if form.is_valid():
            program = form.save()
            messages.success(request, f'Program studi "{program.nama}" berhasil diperbarui.')
            return redirect('ami:program_studi_list')
    else:
        form = ProgramStudiForm(instance=program)
    
    return render(request, 'ami/program_studi_form.html', {
        'form': form,
        'title': f'Edit {program.nama}'
    })

@login_required
def program_studi_delete(request, pk):
    """View untuk menghapus program studi"""
    program = get_object_or_404(ProgramStudi, pk=pk)
    
    if request.method == 'POST':
        nama = program.nama
        program.delete()
        messages.success(request, f'Program studi "{nama}" berhasil dihapus.')
        return redirect('ami:program_studi_list')
    
    return render(request, 'ami/program_studi_confirm_delete.html', {
        'program': program
    })

# ----------------------------
# Views untuk Auditor
# ----------------------------
@login_required
def auditor_list(request):
    """View untuk menampilkan daftar auditor"""
    auditor_list = Auditor.objects.select_related('user').all().order_by('nama_lengkap')
    
    # Pagination
    paginator = Paginator(auditor_list, 10)
    page_number = request.GET.get('page')
    auditor = paginator.get_page(page_number)
    
    return render(request, 'ami/auditor_list.html', {
        'auditor': auditor
    })

@login_required
def auditor_create(request):
    """View untuk membuat auditor baru"""
    if request.method == 'POST':
        form = AuditorForm(request.POST)
        if form.is_valid():
            auditor = form.save()
            messages.success(request, f'Auditor "{auditor.nama_lengkap}" berhasil dibuat.')
            return redirect('ami:auditor_list')
    else:
        form = AuditorForm()
    
    return render(request, 'ami/auditor_form.html', {
        'form': form,
        'title': 'Tambah Auditor'
    })

@login_required
def auditor_update(request, pk):
    """View untuk memperbarui auditor"""
    auditor = get_object_or_404(Auditor, pk=pk)
    
    if request.method == 'POST':
        form = AuditorForm(request.POST, instance=auditor)
        if form.is_valid():
            auditor = form.save()
            messages.success(request, f'Auditor "{auditor.nama_lengkap}" berhasil diperbarui.')
            return redirect('ami:auditor_list')
    else:
        form = AuditorForm(instance=auditor)
    
    return render(request, 'ami/auditor_form.html', {
        'form': form,
        'title': f'Edit {auditor.nama_lengkap}'
    })

# ----------------------------
# Views untuk Audit Session
# ----------------------------
@login_required
def audit_session_list(request):
    """View untuk menampilkan daftar sesi audit"""
    audit_session_list = AuditSession.objects.select_related(
        'program_studi', 'auditor_ketua'
    ).prefetch_related('auditor_anggota').all().order_by('-tanggal_mulai')
    
    # Filter berdasarkan program studi jika ada parameter
    program_studi_id = request.GET.get('program_studi')
    if program_studi_id:
        audit_session_list = audit_session_list.filter(program_studi_id=program_studi_id)
    
    # Pagination
    paginator = Paginator(audit_session_list, 10)
    page_number = request.GET.get('page')
    audit_sessions = paginator.get_page(page_number)
    
    # Ambil semua program studi untuk filter
    program_studi = ProgramStudi.objects.all().order_by('nama')
    
    return render(request, 'ami/audit_session_list.html', {
        'audit_sessions': audit_sessions,
        'program_studi': program_studi
    })

@login_required
def audit_session_create(request):
    """View untuk membuat sesi audit baru"""
    if request.method == 'POST':
        form = AuditSessionForm(request.POST)
        if form.is_valid():
            audit_session = form.save()
            messages.success(request, f'Sesi audit untuk {audit_session.program_studi} berhasil dibuat.')
            return redirect('ami:audit_session_list')
    else:
        form = AuditSessionForm()
    
    return render(request, 'ami/audit_session_form.html', {
        'form': form,
        'title': 'Tambah Sesi Audit'
    })

@login_required
def audit_session_detail(request, pk):
    """View untuk detail sesi audit"""
    audit_session = get_object_or_404(AuditSession, pk=pk)
    
    # Periksa izin akses
    if not check_audit_session_permission(request.user, audit_session):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
    
    # Ambil data penilaian diri
    penilaian_diri = PenilaianDiri.objects.filter(
        audit_session=audit_session
    ).select_related(
        'indikator', 'indikator__elemen', 'indikator__elemen__kriteria'
    ).order_by('indikator__kode')
    
    # Hitung statistik
    total_indikator = penilaian_diri.count()
    indikator_terisi = penilaian_diri.exclude(skor__isnull=True).count()
    persentase_terisi = (indikator_terisi / total_indikator * 100) if total_indikator > 0 else 0
    
    # Ambil data audit
    audit_items = Audit.objects.filter(
        penilaian_diri__audit_session=audit_session
    ).select_related(
        'penilaian_diri', 'penilaian_diri__indikator', 'auditor'
    )
    
    # Hitung statistik audit
    total_audit = audit_items.count()
    audit_selesai = audit_items.exclude(skor__isnull=True).count()
    persentase_audit = (audit_selesai / total_audit * 100) if total_audit > 0 else 0
    
    context = {
        'audit_session': audit_session,
        'penilaian_diri': penilaian_diri,
        'audit_items': audit_items,
        'total_indikator': total_indikator,
        'indikator_terisi': indikator_terisi,
        'persentase_terisi': persentase_terisi,
        'total_audit': total_audit,
        'audit_selesai': audit_selesai,
        'persentase_audit': persentase_audit,
    }
    
    return render(request, 'ami/audit_session_detail.html', context)

@login_required
def audit_session_update(request, pk):
    """View untuk memperbarui sesi audit"""
    audit_session = get_object_or_404(AuditSession, pk=pk)
    
    if request.method == 'POST':
        form = AuditSessionForm(request.POST, instance=audit_session)
        if form.is_valid():
            audit_session = form.save()
            messages.success(request, f'Sesi audit untuk {audit_session.program_studi} berhasil diperbarui.')
            return redirect('ami:audit_session_list')
    else:
        form = AuditSessionForm(instance=audit_session)
    
    return render(request, 'ami/audit_session_form.html', {
        'form': form,
        'title': f'Edit Sesi Audit {audit_session.program_studi}'
    })

@login_required
def audit_session_delete(request, pk):
    """View untuk menghapus sesi audit"""
    audit_session = get_object_or_404(AuditSession, pk=pk)
    
    if request.method == 'POST':
        program_studi = audit_session.program_studi
        tahun_akademik = audit_session.tahun_akademik
        semester = audit_session.semester
        audit_session.delete()
        messages.success(request, f'Sesi audit untuk {program_studi} ({tahun_akademik} {semester}) berhasil dihapus.')
        return redirect('ami:audit_session_list')
    
    return render(request, 'ami/audit_session_confirm_delete.html', {
        'audit_session': audit_session
    })

# ----------------------------
# Views untuk Penilaian Diri
# ----------------------------
@login_required
def penilaian_diri_list(request, session_id):
    """View untuk menampilkan daftar penilaian diri"""
    audit_session = get_object_or_404(AuditSession, pk=session_id)
    
    # Periksa izin akses
    if not check_audit_session_permission(request.user, audit_session):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
    
    penilaian_diri = PenilaianDiri.objects.filter(
        audit_session=audit_session
    ).select_related(
        'indikator', 'indikator__elemen', 'indikator__elemen__kriteria'
    ).order_by('indikator__kode')
    
    context = {
        'audit_session': audit_session,
        'penilaian_diri': penilaian_diri
    }
    
    return render(request, 'ami/penilaian_diri_list.html', context)

@login_required
def penilaian_diri_create(request, session_id):
    """View untuk membuat penilaian diri baru"""
    audit_session = get_object_or_404(AuditSession, pk=session_id)
    
    # Periksa izin akses - hanya program studi yang bersangkutan yang bisa mengisi
    if not check_program_studi_permission(request.user, audit_session.program_studi):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengisi penilaian diri ini.")
    
    if request.method == 'POST':
        form = PenilaianDiriForm(request.POST, request.FILES)
        if form.is_valid():
            penilaian = form.save(commit=False)
            penilaian.audit_session = audit_session
            penilaian.save()
            
            # Jika ada file dokumen pendukung yang diunggah
            if 'bukti_dokumen' in request.FILES:
                dokumen = DokumenPendukung(
                    penilaian_diri=penilaian,
                    nama=f"Dokumen Pendukung {penilaian.indikator.kode}",
                    file=request.FILES['bukti_dokumen'],
                    deskripsi="Dokumen pendukung yang diunggah bersama penilaian"
                )
                dokumen.save()
                
            messages.success(request, 'Penilaian diri berhasil disimpan.')
            return redirect('ami:penilaian_diri_list', session_id=session_id)
    else:
        form = PenilaianDiriForm()
    
    return render(request, 'ami/penilaian_diri_form.html', {
        'form': form,
        'audit_session': audit_session,
        'title': f'Tambah Penilaian Diri - {audit_session.program_studi}'
    })

@login_required
def penilaian_diri_update(request, pk):
    """View untuk memperbarui penilaian diri"""
    penilaian = get_object_or_404(PenilaianDiri, pk=pk)
    audit_session = penilaian.audit_session
    
    # Periksa izin akses - hanya program studi yang bersangkutan yang bisa mengisi
    if not check_program_studi_permission(request.user, audit_session.program_studi):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengubah penilaian diri ini.")
    
    if request.method == 'POST':
        form = PenilaianDiriForm(request.POST, request.FILES, instance=penilaian)
        if form.is_valid():
            penilaian = form.save()
            
            # Jika ada file dokumen pendukung yang diunggah
            if 'bukti_dokumen' in request.FILES:
                dokumen = DokumenPendukung(
                    penilaian_diri=penilaian,
                    nama=f"Dokumen Pendukung {penilaian.indikator.kode}",
                    file=request.FILES['bukti_dokumen'],
                    deskripsi="Dokumen pendukung yang diunggah bersama penilaian"
                )
                dokumen.save()
                
            messages.success(request, 'Penilaian diri berhasil diperbarui.')
            return redirect('ami:penilaian_diri_list', session_id=audit_session.id)
    else:
        form = PenilaianDiriForm(instance=penilaian)
    
    return render(request, 'ami/penilaian_diri_form.html', {
        'form': form,
        'audit_session': audit_session,
        'title': f'Edit Penilaian Diri - {audit_session.program_studi}'
    })

# ----------------------------
# Views untuk Audit
# ----------------------------
@login_required
def audit_list(request, session_id):
    """View untuk menampilkan daftar hasil audit"""
    audit_session = get_object_or_404(AuditSession, pk=session_id)
    
    # Periksa izin akses - hanya auditor yang ditunjuk yang bisa mengakses
    if not check_audit_session_permission(request.user, audit_session):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
    
    audit_items = Audit.objects.filter(
        penilaian_diri__audit_session=audit_session
    ).select_related(
        'penilaian_diri', 
        'penilaian_diri__indikator',
        'penilaian_diri__indikator__elemen',
        'auditor'
    ).order_by('penilaian_diri__indikator__kode')
    
    context = {
        'audit_session': audit_session,
        'audit_items': audit_items
    }
    
    return render(request, 'ami/audit_list.html', context)

@login_required
def audit_update(request, pk):
    """View untuk memperbarui hasil audit"""
    audit_item = get_object_or_404(Audit, pk=pk)
    penilaian_diri = audit_item.penilaian_diri
    audit_session = penilaian_diri.audit_session
    
    # Periksa izin akses - hanya auditor yang ditunjuk yang bisa mengakses
    if not check_audit_session_permission(request.user, audit_session):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengubah audit ini.")
    
    if request.method == 'POST':
        form = AuditForm(request.POST, instance=audit_item)
        if form.is_valid():
            audit = form.save(commit=False)
            # Set auditor ke user yang sedang login
            user_auditor = get_user_auditor(request.user)
            if user_auditor:
                audit.auditor = user_auditor
            audit.save()
            messages.success(request, 'Hasil audit berhasil diperbarui.')
            return redirect('ami:audit_list', session_id=audit_session.id)
    else:
        form = AuditForm(instance=audit_item)
    
    return render(request, 'ami/audit_form.html', {
        'form': form,
        'audit_session': audit_session,
        'penilaian_diri': penilaian_diri,
        'title': f'Audit - {audit_session.program_studi} - {penilaian_diri.indikator.kode}'
    })

# ----------------------------
# Views untuk Dokumen Pendukung
# ----------------------------
@login_required
def dokumen_pendukung_create(request, penilaian_id):
    """View untuk menambah dokumen pendukung"""
    penilaian = get_object_or_404(PenilaianDiri, pk=penilaian_id)
    audit_session = penilaian.audit_session
    
    # Periksa izin akses
    if not check_program_studi_permission(request.user, audit_session.program_studi):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengunggah dokumen pendukung ini.")
    
    if request.method == 'POST':
        form = DokumenPendukungForm(request.POST, request.FILES)
        if form.is_valid():
            dokumen = form.save(commit=False)
            dokumen.penilaian_diri = penilaian
            dokumen.save()
            messages.success(request, 'Dokumen pendukung berhasil diunggah.')
            return redirect('ami:penilaian_diri_list', session_id=audit_session.id)
    else:
        form = DokumenPendukungForm()
    
    return render(request, 'ami/dokumen_pendukung_form.html', {
        'form': form,
        'penilaian': penilaian,
        'title': f'Unggah Dokumen Pendukung - {penilaian.indikator.kode}'
    })

@login_required
def dokumen_pendukung_delete(request, pk):
    """View untuk menghapus dokumen pendukung"""
    dokumen = get_object_or_404(DokumenPendukung, pk=pk)
    penilaian = dokumen.penilaian_diri
    audit_session = penilaian.audit_session
    
    # Periksa izin akses
    if not check_program_studi_permission(request.user, audit_session.program_studi):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk menghapus dokumen ini.")
    
    if request.method == 'POST':
        nama = dokumen.nama
        dokumen.delete()
        messages.success(request, f'Dokumen "{nama}" berhasil dihapus.')
        return redirect('ami:penilaian_diri_list', session_id=audit_session.id)
    
    return render(request, 'ami/dokumen_pendukung_confirm_delete.html', {
        'dokumen': dokumen
    })

# ----------------------------
# Views untuk Rekomendasi Tindak Lanjut
# ----------------------------
@login_required
def rekomendasi_tindak_lanjut_list(request, session_id):
    """View untuk menampilkan daftar rekomendasi tindak lanjut"""
    audit_session = get_object_or_404(AuditSession, pk=session_id)
    
    # Periksa izin akses
    if not check_audit_session_permission(request.user, audit_session):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
    
    rekomendasi = RekomendasiTindakLanjut.objects.filter(
        audit__penilaian_diri__audit_session=audit_session
    ).select_related(
        'audit', 'audit__penilaian_diri', 'audit__penilaian_diri__indikator'
    ).order_by('-tenggat_waktu')
    
    context = {
        'audit_session': audit_session,
        'rekomendasi': rekomendasi
    }
    
    return render(request, 'ami/rekomendasi_tindak_lanjut_list.html', context)

@login_required
def rekomendasi_tindak_lanjut_update(request, pk):
    """View untuk memperbarui rekomendasi tindak lanjut"""
    rekomendasi = get_object_or_404(RekomendasiTindakLanjut, pk=pk)
    audit = rekomendasi.audit
    audit_session = audit.penilaian_diri.audit_session
    
    # Periksa izin akses - hanya program studi yang bersangkutan yang bisa memperbarui status
    if not check_program_studi_permission(request.user, audit_session.program_studi):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk memperbarui rekomendasi ini.")
    
    if request.method == 'POST':
        form = RekomendasiTindakLanjutForm(request.POST, request.FILES, instance=rekomendasi)
        if form.is_valid():
            rekomendasi = form.save()
            messages.success(request, 'Rekomendasi tindak lanjut berhasil diperbarui.')
            return redirect('ami:rekomendasi_tindak_lanjut_list', session_id=audit_session.id)
    else:
        form = RekomendasiTindakLanjutForm(instance=rekomendasi)
    
    return render(request, 'ami/rekomendasi_tindak_lanjut_form.html', {
        'form': form,
        'audit_session': audit_session,
        'rekomendasi': rekomendasi,
        'title': f'Update Tindak Lanjut - {audit_session.program_studi}'
    })

# ----------------------------
# View untuk Laporan
# ----------------------------
@login_required
def laporan_audit(request, session_id):
    """View untuk menampilkan laporan audit"""
    audit_session = get_object_or_404(AuditSession, pk=session_id)
    
    # Periksa izin akses
    if not check_audit_session_permission(request.user, audit_session):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses laporan ini.")
    
    # Ambil semua penilaian diri dan hasil audit
    penilaian_diri_list = PenilaianDiri.objects.filter(
        audit_session=audit_session
    ).select_related(
        'indikator', 'indikator__elemen', 'indikator__elemen__kriteria'
    ).prefetch_related(
        'dokumen_pendukung'
    ).order_by('indikator__kode')
    
    # Hitung statistik untuk laporan
    total_indikator = penilaian_diri_list.count()
    indikator_terisi = penilaian_diri_list.exclude(skor__isnull=True).count()
    persentase_terisi = (indikator_terisi / total_indikator * 100) if total_indikator > 0 else 0
    
    # Hitung skor per kriteria
    kriteria_scores = []
    kriteria_list = audit_session.program_studi.lembaga_akreditasi.kriteria.all()
    
    for kriteria in kriteria_list:
        total_skor = 0
        count = 0
        
        for elemen in kriteria.elemen.all():
            for indikator in elemen.indikator.all():
                try:
                    penilaian = PenilaianDiri.objects.get(
                        audit_session=audit_session,
                        indikator=indikator
                    )
                    if penilaian.skor is not None:
                        total_skor += penilaian.skor
                        count += 1
                except PenilaianDiri.DoesNotExist:
                    pass
        
        if count > 0:
            rata_rata = total_skor / count
            kriteria_scores.append({
                'kriteria': kriteria,
                'rata_rata': round(rata_rata, 2),
                'count': count
            })
    
    # Hitung skor keseluruhan
    total_skor = sum(item['rata_rata'] * item['count'] for item in kriteria_scores)
    total_count = sum(item['count'] for item in kriteria_scores)
    skor_akhir = round(total_skor / total_count, 2) if total_count > 0 else 0
    
    context = {
        'audit_session': audit_session,
        'penilaian_diri_list': penilaian_diri_list,
        'total_indikator': total_indikator,
        'indikator_terisi': indikator_terisi,
        'persentase_terisi': persentase_terisi,
        'kriteria_scores': kriteria_scores,
        'skor_akhir': skor_akhir,
    }
    
    return render(request, 'ami/laporan_audit.html', context)