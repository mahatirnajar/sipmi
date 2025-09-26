# ami/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden, Http404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.db.models import Avg, Count

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
)
from .forms import (
    LembagaAkreditasiForm,
    ProgramStudiForm,
    AuditorForm,
    AuditSessionForm,
    PenilaianDiriForm,
    AuditForm,
    DokumenPendukungForm,
    RekomendasiTindakLanjutForm,
    KriteriaForm,
    ElemenForm,
    KoordinatorProgramStudiForm,
)
# ----------------------------
# Helper Functions
# ----------------------------
def get_user_program_studi(user):
    """Mendapatkan program studi yang terkait dengan user"""
    try:
        # Perbaikan: Mengakses program_studi dari KoordinatorProgramStudi
        if hasattr(user, 'koordinatorprogramstudi'):
            return user.koordinatorprogramstudi.program_studi
        return None
    except AttributeError:
        return None
    
# def get_user_program_studi(user):
#     """Mendapatkan program studi yang terkait dengan user"""
#     try:
#         return user.programstudi
#     except AttributeError:
#         return None

def get_user_auditor(user):
    """Mendapatkan objek auditor yang terkait dengan user"""
    try:
        return user.auditor
    except AttributeError:
        return None

def check_program_studi_permission(user, program_studi):
    """Memeriksa apakah user memiliki izin untuk mengakses program studi tertentu"""
    # if user.is_superuser:
    #     return True
    user_program_studi = get_user_program_studi(user)
    return user_program_studi == program_studi

def check_audit_session_permission(user, audit_session):
    """Memeriksa apakah user memiliki izin untuk mengakses sesi audit tertentu"""
    if user.is_superuser:
        return True

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
    latest_audit_sessions = AuditSession.objects.select_related('program_studi').order_by('-tanggal_mulai_penilaian_mandiri')[:5]
    latest_penilaian_diri = PenilaianDiri.objects.select_related(
        'audit_session', 'audit_session__program_studi', 'elemen'
    ).order_by('-tanggal_penilaian')[:5]
    
    # # Data untuk grafik
    # kriteria_data = []
    # if latest_audit_sessions:
    #     # Ambil sesi audit terbaru untuk data grafik
    #     latest_session = latest_audit_sessions[0]
    #     kriteria_list = latest_session.program_studi.lembaga_akreditasi.kriteria.all()
        
    #     for kriteria in kriteria_list:
    #         # Hitung rata-rata skor untuk kriteria ini
    #         total_skor = 0
    #         count = 0
            
    #         for elemen in kriteria.elemen.all():
    #             for indikator in elemen.indikator.all():
    #                 try:
    #                     penilaian = PenilaianDiri.objects.get(
    #                         audit_session=latest_session,
    #                         indikator=indikator
    #                     )
    #                     if penilaian.skor is not None:
    #                         total_skor += penilaian.skor
    #                         count += 1
    #                 except PenilaianDiri.DoesNotExist:
    #                     pass
            
    #         if count > 0:
    #             rata_rata = total_skor / count
    #             kriteria_data.append({
    #                 'nama': kriteria.nama,
    #                 'rata_rata': round(rata_rata, 2)
    #             })
    
    context = {
        'total_program_studi': total_program_studi,
        'total_audit_session': total_audit_session,
        'total_penilaian_diri': total_penilaian_diri,
        'total_audit': total_audit,
        'latest_audit_sessions': latest_audit_sessions,
        'latest_penilaian_diri': latest_penilaian_diri,
        # 'kriteria_data': kriteria_data,
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
def lembaga_akreditasi_detail(request, pk):
    """View untuk detail lembaga akreditasi beserta kriterianya"""
    lembaga = get_object_or_404(LembagaAkreditasi, pk=pk)
    kriteria_list = lembaga.kriteria.all().order_by('kode')
    
    # Pagination
    paginator = Paginator(kriteria_list, 10)
    page_number = request.GET.get('page')
    kriteria = paginator.get_page(page_number)
    
    return render(request, 'ami/lembaga_akreditasi_detail.html', {
        'lembaga': lembaga,
        'kriteria': kriteria
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
    audit_sessions = program.audit_sessions.all().order_by('-tanggal_mulai_penilaian_mandiri')
    
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
# Views untuk Koordinator Program Studi
# ----------------------------
@login_required
def koordinator_list(request):
    """View untuk menampilkan daftar koordinator program studi"""
    koordinators = KoordinatorProgramStudi.objects.select_related('user', 'program_studi').all().order_by('nama_lengkap')
    # Pagination
    paginator = Paginator(koordinators, 10)
    page_number = request.GET.get('page')
    koordinator_list = paginator.get_page(page_number)
    return render(request, 'ami/koordinator_list.html', {
        'koordinator_list': koordinator_list
    })

@login_required
def koordinator_create(request):
    """View untuk membuat koordinator program studi baru"""
    if request.method == 'POST':
        form = KoordinatorProgramStudiForm(request.POST)
        if form.is_valid():
            nuptk = form.cleaned_data['nuptk']
            nama_lengkap = form.cleaned_data['nama_lengkap']
            program_studi = form.cleaned_data['program_studi']
            
            # Cek apakah NUPTK sudah ada sebagai username
            if User.objects.filter(username=nuptk).exists():
                form.add_error('nuptk', 'NUPTK sudah digunakan')
            else:
                 # Pisahkan nama menjadi first_name dan last_name
                name_parts = nama_lengkap.split()
                first_name = name_parts[0] if name_parts else ''
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

                # Buat user dengan username dan password = nuptk
                user = User.objects.create_user(
                    username=nuptk,
                    first_name=first_name,
                    last_name=last_name,
                    password=nuptk  # Django akan meng-hash password secara otomatis
                )
                
                user.save()

                # Buat koordinator program studi
                koordinator = form.save(commit=False)
                koordinator.user=user
                koordinator.save()
                
                messages.success(request, f'Koordinator "{koordinator.nama_lengkap}" berhasil dibuat.')
                return redirect('ami:koordinator_list')
    else:
        form = KoordinatorProgramStudiForm()
    return render(request, 'ami/koordinator_form.html', {
        'form': form,
        'title': 'Tambah Koordinator Program Studi'
    })

@login_required
def koordinator_detail(request, pk):
    """View untuk detail koordinator program studi"""
    koordinator = get_object_or_404(KoordinatorProgramStudi, pk=pk)
    return render(request, 'ami/koordinator_detail.html', {
        'koordinator': koordinator
    })

@login_required
def koordinator_update(request, pk):
    """View untuk memperbarui koordinator program studi"""
    koordinator = get_object_or_404(KoordinatorProgramStudi, pk=pk)
    if request.method == 'POST':
        form = KoordinatorProgramStudiForm(request.POST, instance=koordinator)
        if form.is_valid():
            koordinator = form.save(commit=False)
            
            # Jika nuptk berubah, kita perlu memperbarui username user
            if koordinator.nuptk != koordinator.user.username:
                # Cek apakah NUPTK baru sudah ada sebagai username
                if User.objects.filter(username=koordinator.nuptk).exists():
                    form.add_error('nuptk', 'NUPTK sudah digunakan sebagai username')
                else:
                    koordinator.user.username = koordinator.nuptk
                    koordinator.user.save()
            
            koordinator.save()
            messages.success(request, f'Koordinator "{koordinator.nama_lengkap}" berhasil diperbarui.')
            return redirect('ami:koordinator_list')
    else:
        form = KoordinatorProgramStudiForm(instance=koordinator)
    return render(request, 'ami/koordinator_form.html', {
        'form': form,
        'title': f'Edit {koordinator.nama_lengkap}'
    })

@login_required
def koordinator_delete(request, pk):
    """View untuk menghapus koordinator program studi"""
    koordinator = get_object_or_404(KoordinatorProgramStudi, pk=pk)
    if request.method == 'POST':
        nama = koordinator.nama_lengkap
        # Hapus user terkait
        user = koordinator.user
        koordinator.delete()
        user.delete()
        messages.success(request, f'Koordinator "{nama}" berhasil dihapus.')
        return redirect('ami:koordinator_list')
    return render(request, 'ami/koordinator_confirm_delete.html', {
        'koordinator': koordinator
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
             # Ambil data dari form
            nuptk = form.cleaned_data['nuptk']
            nama_lengkap = form.cleaned_data['nama_lengkap']
            
            # Pisahkan nama menjadi first_name dan last_name
            name_parts = nama_lengkap.split()
            first_name = name_parts[0] if name_parts else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            # Buat user baru
            user = User.objects.create_user(
                username=nuptk,
                first_name=first_name,
                last_name=last_name,
                password='abcde'  # Password acak
            )
            user.save()

            auditor = form.save(commit=False)
            auditor.user=user
            auditor.save()

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
    
    # Dapatkan informasi user
    user_program_studi = get_user_program_studi(request.user)
    user_auditor = get_user_auditor(request.user)
    
    # Mulai dengan semua sesi audit
    audit_session_list = AuditSession.objects.select_related(
        'program_studi', 'auditor_ketua'
    ).prefetch_related('auditor_anggota').all()
    
    # Filter berdasarkan peran user (hanya membatasi sesi yang ditampilkan, tidak menghapus dari daftar)
    if not request.user.is_superuser:
        if user_program_studi:
            # Koordinator program studi hanya melihat sesi audit untuk program studi mereka
            audit_session_list = audit_session_list.filter(program_studi=user_program_studi)
        elif user_auditor:
            # Auditor hanya melihat sesi audit yang mereka ditugaskan
            audit_session_list = audit_session_list.filter(
                Q(auditor_ketua=user_auditor) | Q(auditor_anggota=user_auditor)
            ).distinct()
    
    # Filter berdasarkan program studi jika ada parameter
    program_studi_id = request.GET.get('program_studi')
    if program_studi_id:
        audit_session_list = audit_session_list.filter(program_studi_id=program_studi_id)

    # Filter berdasarkan Lembaga Akreditasi
    lembaga = request.GET.get('lembaga')
    if lembaga:
        audit_session_list = audit_session_list.filter(program_studi_id__lembaga_akreditasi=lembaga)
        


    
    # Urutkan
    audit_session_list = audit_session_list.order_by('-tanggal_mulai_penilaian_mandiri')
    
    # Pagination
    paginator = Paginator(audit_session_list, 10)
    page_number = request.GET.get('page')
    audit_sessions = paginator.get_page(page_number)
    
    # Ambil semua program studi untuk filter
    program_studi = ProgramStudi.objects.all().order_by('nama')
    lembaga = LembagaAkreditasi.objects.all().order_by('nama')

    
    return render(request, 'ami/audit_session_list.html', {
        'audit_sessions': audit_sessions,
        'program_studi': program_studi,
        'user_program_studi': user_program_studi,
        'user_auditor': user_auditor,
        'lembaga': lembaga
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
    # Perbarui status berdasarkan tanggal

    audit_session.update_status()
    # Periksa izin akses
    if not check_audit_session_permission(request.user, audit_session):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
    
    # Ambil semua elemen dari lembaga akreditasi prodi
    lembaga = audit_session.program_studi.lembaga_akreditasi
    semua_elemen = Elemen.objects.filter(kriteria__lembaga_akreditasi=lembaga).order_by('kode')
    
    # Untuk setiap elemen, pastikan ada penilaian diri
    penilaian_diri_list = []
    for elemen in semua_elemen:
        penilaian, created = PenilaianDiri.objects.get_or_create(
            audit_session=audit_session,
            elemen=elemen,
            defaults={
                'status': 'BELUM'
            }
        )
        penilaian_diri_list.append(penilaian)
    
    # Hitung statistik
    total_indikator = len(penilaian_diri_list)
    indikator_terisi = sum(1 for p in penilaian_diri_list if p.skor is not None)
    persentase_terisi = (indikator_terisi / total_indikator * 100) if total_indikator > 0 else 0
    
    # Ambil data audit
    audit_items = Audit.objects.filter(
        penilaian_diri__in=penilaian_diri_list
    ).select_related(
        'auditor'
    )
    
    # Hitung statistik audit
    total_audit = audit_items.count()
    audit_selesai = audit_items.exclude(skor__isnull=True).count()
    persentase_audit = (audit_selesai / total_audit * 100) if total_audit > 0 else 0
    
    context = {
        'audit_session': audit_session,
        'penilaian_diri': penilaian_diri_list,
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
    
    # Ambil semua elemen dari lembaga akreditasi prodi
    lembaga = audit_session.program_studi.lembaga_akreditasi
    semua_elemen = Elemen.objects.filter(
        kriteria__lembaga_akreditasi=lembaga,
        status='aktif'
    ).order_by('kriteria__kode', 'kode')
    
    # Untuk setiap elemen, pastikan ada penilaian diri
    grouped_data = {}
    elemen_count = 0
    elemen_terisi = 0
    
    for elemen in semua_elemen:
        elemen_count += 1
        # Dapatkan atau buat penilaian diri
        penilaian, created = PenilaianDiri.objects.get_or_create(
            audit_session=audit_session,
            elemen=elemen,
            defaults={
                'status': 'BELUM'
            }
        )
        
        # Cek apakah elemen sudah terisi
        if penilaian.skor is not None:
            elemen_terisi += 1
        
        # Kelompokkan berdasarkan kriteria
        kriteria = elemen.kriteria
        if kriteria not in grouped_data:
            grouped_data[kriteria] = []
        grouped_data[kriteria].append(penilaian)
    
    # Hitung statistik
    persentase_terisi = (elemen_terisi / elemen_count * 100) if elemen_count > 0 else 0
    
    context = {
        'audit_session': audit_session,
        'grouped_data': grouped_data,
        'total_elemen': elemen_count,
        'elemen_terisi': elemen_terisi,
        'persentase_terisi': persentase_terisi
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
            
            # # Jika ada file dokumen pendukung yang diunggah
            # if 'bukti_dokumen' in request.FILES:
            #     dokumen = DokumenPendukung(
            #         penilaian_diri=penilaian,
            #         nama=f"Dokumen Pendukung {penilaian.indikator.kode}",
            #         file=request.FILES['bukti_dokumen'],
            #         deskripsi="Dokumen pendukung yang diunggah bersama penilaian"
            #     )
            #     dokumen.save()
                
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
    
    # # Periksa status sesi audit
    # if audit_session.status not in ['DRAFT', 'PENILAIAN_MANDIRI']:
    #     messages.error(request, "Penilaian hanya bisa diubah saat status sesi adalah 'Draft' atau 'Penilaian Mandiri'.")
    #     return redirect('ami:penilaian_diri_list', session_id=audit_session.id)
    
    # # Periksa apakah masih dalam rentang tanggal penilaian mandiri
    # today = timezone.now().date()
    # if audit_session.tanggal_mulai_penilaian_mandiri and audit_session.tanggal_selesai_penilaian_mandiri:
    #     if today < audit_session.tanggal_mulai_penilaian_mandiri or today > audit_session.tanggal_selesai_penilaian_mandiri:
    #         messages.error(request, "Penilaian hanya bisa diubah dalam rentang tanggal penilaian mandiri.")
    #         return redirect('ami:penilaian_diri_list', session_id=audit_session.id)
    
    if request.method == 'POST':
        form = PenilaianDiriForm(request.POST, instance=penilaian)
        if form.is_valid():
            penilaian = form.save()
            # Update status penilaian
            if penilaian.skor is not None:
                penilaian.status = 'TERISI'
                penilaian.save()
            
            messages.success(request, 'Penilaian diri berhasil diperbarui.')
            return redirect('ami:penilaian_diri_list', session_id=audit_session.id)
    else:
        form = PenilaianDiriForm(instance=penilaian)
    
    context = {
        'form': form,
        'audit_session': audit_session,
        'penilaian': penilaian,
        'title': f'Edit Penilaian Diri - {audit_session.program_studi}'
    }
    return render(request, 'ami/penilaian_diri_form.html', context)

@login_required
def submit_penilaian_diri(request, session_id):
    """View untuk mengirim penilaian diri dan mengubah status sesi audit"""
    audit_session = get_object_or_404(AuditSession, pk=session_id)
    
    # Periksa izin akses - hanya program studi yang bersangkutan yang bisa mengirim
    if not check_program_studi_permission(request.user, audit_session.program_studi):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengirim penilaian ini.")
    
    # Periksa status saat ini
    if audit_session.status != 'PENILAIAN_MANDIRI':
        messages.error(request, "Penilaian hanya bisa dikirim saat status sesi adalah 'Penilaian Mandiri'.")
        return redirect('ami:audit_session_list')
    
    # Periksa apakah semua penilaian sudah terisi
    penilaian_diri = PenilaianDiri.objects.filter(audit_session=audit_session)
    belum_terisi = penilaian_diri.filter(skor__isnull=True).count()
    
    if belum_terisi > 0:
        messages.error(request, f"Masih ada {belum_terisi} elemen yang belum dinilai. Silakan lengkapi semua penilaian terlebih dahulu.")
        return redirect('ami:audit_session_list')
    
    # Ubah status penilaian diri menjadi 'DIAJUKAN'
    penilaian_diri.update(status='DIAJUKAN')
    
    # Ubah status sesi audit menjadi 'PENILAIAN_AUDITOR'
    audit_session.status = 'PENILAIAN_AUDITOR'
    audit_session.save()
    
    messages.success(request, "Penilaian diri berhasil dikirim. Sesi audit sekarang dalam status 'Penilaian Auditor'.")
    return redirect('ami:audit_session_list')

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
    
    # Ambil semua elemen dari lembaga akreditasi prodi
    lembaga = audit_session.program_studi.lembaga_akreditasi
    semua_elemen = Elemen.objects.filter(
        kriteria__lembaga_akreditasi=lembaga,
        status='aktif'
    ).order_by('kriteria__kode', 'kode')
    
    # Untuk setiap elemen, pastikan ada penilaian diri dan audit
    grouped_data = {}
    elemen_count = 0
    elemen_teraudit = 0
    
    for elemen in semua_elemen:
        elemen_count += 1
        # Dapatkan atau buat penilaian diri
        penilaian_diri, created = PenilaianDiri.objects.get_or_create(
            audit_session=audit_session,
            elemen=elemen,
            defaults={
                'status': 'BELUM'
            }
        )
        
        # Dapatkan atau buat hasil audit
        audit, created = Audit.objects.get_or_create(
            penilaian_diri=penilaian_diri
        )
        
        # Cek apakah elemen sudah diaudit
        if audit.skor is not None:
            elemen_teraudit += 1
        
        # Kelompokkan berdasarkan kriteria
        kriteria = elemen.kriteria
        if kriteria not in grouped_data:
            grouped_data[kriteria] = []
        grouped_data[kriteria].append({
            'elemen': elemen,
            'penilaian_diri': penilaian_diri,
            'audit': audit
        })
    
    # Hitung statistik
    persentase_teraudit = (elemen_teraudit / elemen_count * 100) if elemen_count > 0 else 0
    
    context = {
        'audit_session': audit_session,
        'grouped_data': grouped_data,
        'total_elemen': elemen_count,
        'elemen_teraudit': elemen_teraudit,
        'persentase_teraudit': persentase_teraudit
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
    
    # Periksa apakah user adalah auditor
    user_auditor = get_user_auditor(request.user)
    if not user_auditor:
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengubah audit ini.")
    
    # Periksa status sesi audit
    if audit_session.status != 'PENILAIAN_AUDITOR':
        messages.error(request, "Audit hanya bisa dilakukan saat status sesi adalah 'Penilaian Auditor'.")
        return redirect('ami:audit_list', session_id=audit_session.id)
    
    # Periksa apakah masih dalam rentang tanggal penilaian auditor
    today = timezone.now().date()
    if audit_session.tanggal_mulai_penilaian_auditor and audit_session.tanggal_selesai_penilaian_auditor:
        if today < audit_session.tanggal_mulai_penilaian_auditor or today > audit_session.tanggal_selesai_penilaian_auditor:
            messages.error(request, "Audit hanya bisa dilakukan dalam rentang tanggal penilaian auditor.")
            return redirect('ami:audit_list', session_id=audit_session.id)
    
    if request.method == 'POST':
        form = AuditForm(request.POST, instance=audit_item)
        if form.is_valid():
            audit = form.save(commit=False)
            # Set auditor ke user yang sedang login
            audit.auditor = user_auditor
            audit.save()
            messages.success(request, 'Hasil audit berhasil diperbarui.')
            return redirect('ami:audit_list', session_id=audit_session.id)
    else:
        form = AuditForm(instance=audit_item)
    
    context = {
        'form': form,
        'audit_session': audit_session,
        'penilaian_diri': penilaian_diri,
        'title': f'Audit - {audit_session.program_studi} - {penilaian_diri.elemen.kode}'
    }
    return render(request, 'ami/audit_form.html', context)


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
        'title': f'Unggah Dokumen Pendukung - {penilaian.elemen.kode}'  # Perbaikan: ganti indikator dengan elemen
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
# View untuk Laporan auditi
# ----------------------------
@login_required
def laporan_audit(request, session_id):
    """View untuk menampilkan laporan audit"""
    audit_session = get_object_or_404(AuditSession, pk=session_id)
    # izin akses
    if not check_audit_session_permission(request.user, audit_session):
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses laporan ini.")
    # semua penilaian diri dan hasil audit
    penilaian_diri_list = PenilaianDiri.objects.filter(
        audit_session=audit_session
    ).select_related(
        'elemen', 'elemen__kriteria'  
    ).prefetch_related(
        'dokumen_pendukung'
    ).order_by('elemen__kode')  

    # Hitung statistik untuk laporan
    total_indikator = penilaian_diri_list.count()
    indikator_terisi = penilaian_diri_list.exclude(skor__isnull=True).count()
    persentase_terisi = (indikator_terisi / total_indikator * 100) if total_indikator > 0 else 0
    
    # --- Hitung skor per kriteria untuk tabel ---
    kriteria_scores = []
    kriteria_list = audit_session.program_studi.lembaga_akreditasi.kriteria.all()
    for kriteria in kriteria_list:
        total_skor, count = 0, 0
        for elemen in kriteria.elemen.all():
            try:
                penilaian = PenilaianDiri.objects.get(audit_session=audit_session, elemen=elemen)
                if penilaian.skor is not None:
                    total_skor += float(penilaian.skor)
                    count += 1
            except PenilaianDiri.DoesNotExist:
                pass
        if count > 0:
            kriteria_scores.append({
                "kriteria": kriteria,
                "rata_rata": round(total_skor / count, 2),
                "count": count,
            })
    
    # Hitung skor keseluruhan
    total_skor = sum(item["rata_rata"] * item["count"] for item in kriteria_scores)
    total_count = sum(item["count"] for item in kriteria_scores)
    skor_akhir = round(total_skor / total_count, 2) if total_count > 0 else 0

    # --- Data Radar Chart  ---
    radar_labels, radar_pd = [], []
    for item in kriteria_scores:
        radar_labels.append(item["kriteria"].nama)
        radar_pd.append(item["rata_rata"])

    context = {
        'audit_session': audit_session,
        'penilaian_diri_list': penilaian_diri_list,
        'total_indikator': total_indikator,
        'indikator_terisi': indikator_terisi,
        'persentase_terisi': persentase_terisi,
        'kriteria_scores': kriteria_scores,
        'skor_akhir': skor_akhir,
        "radar_labels": radar_labels,
        "radar_pd": radar_pd,
        
    }
    return render(request, 'ami/laporan_audit.html', context)



@login_required
def laporan_index_audit(request):
    """Index daftar sesi audit untuk melihat laporan"""
    user_program_studi = get_user_program_studi(request.user)
    user_auditor = get_user_auditor(request.user)

    qs = AuditSession.objects.select_related('program_studi', 'auditor_ketua')\
        .prefetch_related('auditor_anggota').all()

    if not request.user.is_superuser:
        if user_program_studi:
            qs = qs.filter(program_studi=user_program_studi)
        elif user_auditor:
            qs = qs.filter(Q(auditor_ketua=user_auditor) | Q(auditor_anggota=user_auditor)).distinct()

   
    program_studi_id = request.GET.get('program_studi')
    if program_studi_id:
        qs = qs.filter(program_studi_id=program_studi_id)

    qs = qs.order_by('-tanggal_mulai_penilaian_mandiri')

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    audit_sessions = paginator.get_page(page_number)

    programs = ProgramStudi.objects.all().order_by('nama')

    return render(request, 'ami/laporan_index_audit.html', {
        'audit_sessions': audit_sessions,
        'program_studi': programs,
        'user_program_studi': user_program_studi,
        'user_auditor': user_auditor
    })




#------------------------------
#  VIEW UNTUK LAPORAN AUDITOR 
#------------------------------
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from .models import AuditSession, Audit,LembagaAkreditasi

@login_required
def laporan_auditor(request, session_id: int):
    """
    Laporan khusus untuk Tim Auditor pada sesi.
    ketua/anggota atau superuser yang dapat akses.
    """
    session = get_object_or_404(
        AuditSession.objects.select_related('program_studi', 'auditor_ketua')
                            .prefetch_related('auditor_anggota'),
        pk=session_id
    )

    # akses
    auditor_profile = getattr(request.user, 'auditor', None)
    if not request.user.is_superuser:
        if auditor_profile is None:
            return HttpResponseForbidden("Halaman dapat diakses oleh auditor.")
        is_ketua = (session.auditor_ketua_id == auditor_profile.id)
        is_anggota = session.auditor_anggota.filter(pk=auditor_profile.id).exists()
        if not (is_ketua or is_anggota):
            return HttpResponseForbidden("Anda tidak memiliki akses untuk melihat laporan auditor.")

    # Data audit 
    audits = (
        Audit.objects
        .select_related(
            'auditor',
            'penilaian_diri',
            'penilaian_diri__elemen',
            'penilaian_diri__elemen__kriteria',
        )
        .filter(penilaian_diri__audit_session=session)
        .order_by(
            'penilaian_diri__elemen__kriteria__nama',  
            'penilaian_diri__elemen__kode'
        )
    )

    # Statistik ringkas
    stats = {
        "total": audits.count(),
        "avg_skor": round(audits.aggregate(v=Avg('skor'))['v'] or 0, 2),
        "kategori": list(
            audits.values('kategori_kondisi')
                  .annotate(jumlah=Count('id'))
                  .order_by()
        ),
    }

    # --- Rekap "Skor per Kriteria (Penilaian Auditor)" ---
    agg = (
        audits.values(
            'penilaian_diri__elemen__kriteria_id',
            'penilaian_diri__elemen__kriteria__nama',
        )
        .annotate(
            # untuk "jumlah indikator"  ganti ke Count('penilaian_diri__indikator_id', distinct=True)
            jumlah_indikator=Count('penilaian_diri__elemen_id', distinct=True),
            rata=Avg('skor'),
        )
        .order_by('penilaian_diri__elemen__kriteria__nama')
    )

    kriteria_scores_auditor = [
        {
            "nama": x["penilaian_diri__elemen__kriteria__nama"],
            "jumlah": x["jumlah_indikator"],
            "rata_rata": round(x["rata"] or 0, 2),
        }
        for x in agg
    ]

    
    ctx = {
        "audit_session": session,
        "audits": audits,
        "stats": stats,
        "kriteria_scores_auditor": kriteria_scores_auditor,
    }
    return render(request, "ami/laporan_auditor.html", ctx)



@login_required
def laporan_index_auditor(request):
    
    auditor = getattr(request.user, 'auditor', None)

    # Jika bukan auditor dan bukan superuser -> tolak
    if not (request.user.is_superuser or auditor):
        return HttpResponseForbidden("Halaman ini khusus untuk auditor.")

    qs = (AuditSession.objects
          .select_related('program_studi',
            'program_studi__lembaga_akreditasi',
            'auditor_ketua')
          .prefetch_related('auditor_anggota')
          .all())

   # --- filters lembaga    ---
    status = request.GET.get('status', '').strip()
    q = request.GET.get('q', '').strip()
    lembaga_id = request.GET.get('lembaga', '').strip()  # dari <select name="lembaga">

    if status:
        qs = qs.filter(status=status)

    if q:
        qs = qs.filter(Q(tahun_akademik__icontains=q) | Q(semester__icontains=q))

    if lembaga_id:
        qs = qs.filter(program_studi__lembaga_akreditasi_id=lembaga_id)
    
    
    qs = qs.order_by('-tanggal_mulai_penilaian_mandiri')

    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ami/laporan_index_auditor.html', {
        'audit_sessions': page_obj,
        'status_selected': status,
        'q': q,
        'lembaga_list': LembagaAkreditasi.objects.all(),  
        'lembaga_selected': lembaga_id,                  
    })

# ----------------------------
# Views untuk Kriteria
# ----------------------------

@login_required
def get_lembaga_kode(request, pk):
    """API untuk mendapatkan kode lembaga berdasarkan ID"""
    lembaga = get_object_or_404(LembagaAkreditasi, pk=pk)
    return JsonResponse({
        'id': lembaga.id,
        'kode': lembaga.kode,
        'nama': lembaga.nama
    })

@login_required
def kriteria_list(request, lembaga_id=None):
    """View untuk menampilkan daftar kriteria berdasarkan lembaga akreditasi"""
    lembaga = None
    if lembaga_id:
        lembaga = get_object_or_404(LembagaAkreditasi, pk=lembaga_id)
        kriteria_list = Kriteria.objects.filter(lembaga_akreditasi=lembaga).order_by('kode')
    else:
        kriteria_list = Kriteria.objects.all().order_by('kode')
    
    # Pagination
    paginator = Paginator(kriteria_list, 10)
    page_number = request.GET.get('page')
    kriteria = paginator.get_page(page_number)
    
    # Ambil semua lembaga akreditasi untuk filter
    lembaga_akreditasi = LembagaAkreditasi.objects.all().order_by('nama')
    
    return render(request, 'ami/kriteria_list.html', {
        'kriteria': kriteria,
        'lembaga_akreditasi': lembaga_akreditasi,
        'selected_lembaga': lembaga
    })

@login_required
def kriteria_create(request, lembaga_id=None):
    """View untuk membuat kriteria baru"""
    # Hanya staff yang bisa mengelola kriteria
    if not request.user.is_staff:
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
        
    lembaga = None
    if lembaga_id:
        lembaga = get_object_or_404(LembagaAkreditasi, pk=lembaga_id)
    print(lembaga)
    if request.method == 'POST':
        form = KriteriaForm(request.POST)
        if form.is_valid():
            kriteria = form.save()
            messages.success(request, f'Kriteria "{kriteria.nama}" berhasil dibuat.')
            return redirect('ami:lembaga_akreditasi_detail', lembaga_id)
    else:
        initial = {'lembaga_akreditasi': lembaga} if lembaga else {}
        form = KriteriaForm(initial=initial)
    
    return render(request, 'ami/kriteria_form.html', {
        'form': form,
        'title': 'Tambah Kriteria',
        'lembaga': lembaga
    })

@login_required
def kriteria_update(request, pk):
    """View untuk memperbarui kriteria"""
    # Hanya staff yang bisa mengelola kriteria
    if not request.user.is_staff:
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
        
    kriteria = get_object_or_404(Kriteria, pk=pk)
    if request.method == 'POST':
        form = KriteriaForm(request.POST, instance=kriteria)
        if form.is_valid():
            kriteria = form.save()
            messages.success(request, f'Kriteria "{kriteria.nama}" berhasil diperbarui.')
            return redirect('ami:lembaga_akreditasi_detail', kriteria.lembaga_akreditasi.id)
    else:
        form = KriteriaForm(instance=kriteria)
    
    return render(request, 'ami/kriteria_form.html', {
        'form': form,
        'title': f'Edit {kriteria.kode} - {kriteria.nama}',
        'lembaga': kriteria.lembaga_akreditasi
    })

@login_required
def kriteria_detail(request, pk):
    """View untuk detail kriteria"""
    kriteria = get_object_or_404(Kriteria, pk=pk)
    elemen_list = kriteria.elemen.all().order_by('kode')
    
    return render(request, 'ami/kriteria_detail.html', {
        'kriteria': kriteria,
        'elemen_list': elemen_list
    })

@login_required
def kriteria_delete(request, pk):
    """View untuk menghapus kriteria"""
    # Hanya staff yang bisa mengelola kriteria
    if not request.user.is_staff:
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
        
    kriteria = get_object_or_404(Kriteria, pk=pk)
    if request.method == 'POST':
        nama = kriteria.nama
        # lembaga_id = kriteria.lembaga_akreditasi.id
        kriteria.delete()
        messages.success(request, f'Kriteria "{nama}" berhasil dihapus.')
        return redirect('ami:lembaga_akreditasi_detail', kriteria.lembaga_akreditasi.id)
    
    return render(request, 'ami/kriteria_confirm_delete.html', {
        'kriteria': kriteria
    })

# ----------------------------
# Views untuk Elemen
# ----------------------------
@login_required
def elemen_list(request, kriteria_id=None):
    """View untuk menampilkan daftar elemen berdasarkan kriteria"""
    kriteria = None
    if kriteria_id:
        kriteria = get_object_or_404(Kriteria, pk=kriteria_id)
        elemen_list = Elemen.objects.filter(kriteria=kriteria).order_by('kode')
    else:
        elemen_list = Elemen.objects.all().order_by('kode')
    
    # Pagination
    paginator = Paginator(elemen_list, 10)
    page_number = request.GET.get('page')
    elemen = paginator.get_page(page_number)
    
    return render(request, 'ami/elemen_list.html', {
        'elemen': elemen,
        'kriteria': kriteria
    })

@login_required
def elemen_create(request, kriteria_id=None):
    """View untuk membuat elemen baru"""
    # Hanya staff yang bisa mengelola elemen
    if not request.user.is_staff:
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
        
    kriteria = None
    if kriteria_id:
        kriteria = get_object_or_404(Kriteria, pk=kriteria_id)
    
    print(kriteria)

    if request.method == 'POST':
        print("masuk post")
        form = ElemenForm(request.POST)
        if form.is_valid():
            print("valid")
            elemen = form.save()
            messages.success(request, f'Elemen "{elemen.nama}" berhasil dibuat.')
            return redirect('ami:kriteria_detail', pk=kriteria_id)
    else:
        initial = {'kriteria': kriteria} if kriteria else {}
        form = ElemenForm(initial=initial)
    
    return render(request, 'ami/elemen_form.html', {
        'form': form,
        'title': 'Tambah Elemen',
        'kriteria': kriteria
    })

@login_required
def elemen_update(request, pk):
    """View untuk memperbarui elemen"""
    # Hanya staff yang bisa mengelola elemen
    if not request.user.is_staff:
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
        
    elemen = get_object_or_404(Elemen, pk=pk)
    if request.method == 'POST':
        print("masuk post")
        form = ElemenForm(request.POST, instance=elemen)
        if form.is_valid():
            print("valid")
            elemen = form.save()
            messages.success(request, f'Elemen "{elemen.nama}" berhasil diperbarui.')
            return redirect('ami:kriteria_detail', pk=elemen.kriteria.id)
    else:
        form = ElemenForm(instance=elemen)
    
    return render(request, 'ami/elemen_form.html', {
        'form': form,
        'title': f'Edit {elemen.kode} - {elemen.nama}',
        'kriteria': elemen.kriteria
    })

@login_required
def elemen_detail(request, pk):
    """View untuk detail elemen"""
    elemen = get_object_or_404(Elemen, pk=pk)
    indikator_list = elemen.indikator.all().order_by('kode')
    
    return render(request, 'ami/elemen_detail.html', {
        'elemen': elemen,
        'indikator_list': indikator_list
    })

@login_required
def elemen_delete(request, pk):
    """View untuk menghapus elemen"""
    # Hanya staff yang bisa mengelola elemen
    if not request.user.is_staff:
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
        
    elemen = get_object_or_404(Elemen, pk=pk)
    if request.method == 'POST':
        nama = elemen.nama
        kriteria_id = elemen.kriteria.id
        elemen.delete()
        messages.success(request, f'Elemen "{nama}" berhasil dihapus.')
        return redirect('ami:kriteria_detail', pk=kriteria_id)
    
    return render(request, 'ami/elemen_confirm_delete.html', {
        'elemen': elemen
    })



#---------------------
#  VIEW UNTUK LAPORAN INTERNAL
#---------------------
import json, re

@login_required
def laporan_internal(request, session_id: int):
    """
    Laporan Internal (cover).
    Akses: superuser , atau auditor yang ditugaskan (ketua/anggota) pada sesi ini.
    """
    # Ambil sesi + relasi penting
    session = get_object_or_404(
        AuditSession.objects.select_related('program_studi', 'auditor_ketua')
                            .prefetch_related('auditor_anggota'),
        pk=session_id
    )

    # akun yang bisa akses
    # - superuser 
    # - auditor yang ditugaskan
    if not (request.user.is_superuser or request.user.is_staff):
        auditor_profile = getattr(request.user, 'auditor', None)
        if not auditor_profile:
            return HttpResponseForbidden("Halaman ini tidak dapat diakses.")
        is_ketua = (session.auditor_ketua_id == auditor_profile.id)
        is_anggota = session.auditor_anggota.filter(pk=auditor_profile.id).exists()
        if not (is_ketua or is_anggota):
            return HttpResponseForbidden("Anda tidak memiliki akses untuk melihat laporan ini.")

    # Data hasil audit (pakai ELEMEN)
    audits = (
        Audit.objects
        .select_related(
            'auditor',
            'penilaian_diri',
            'penilaian_diri__elemen',
            'penilaian_diri__elemen__kriteria',
            
        )
        .filter(penilaian_diri__audit_session=session)
        .order_by('penilaian_diri__elemen__kriteria__nama',
                  'penilaian_diri__elemen__kode')
    )

    #koordinator prodi
    koordinator_prodi = (
        KoordinatorProgramStudi.objects
        .select_related('program_studi')
        .filter(program_studi=session.program_studi)
        .order_by('-id')  
        .first())
    
    # rata-rata kriteria
    kriteria_avg = (
        PenilaianDiri.objects
        .filter(audit_session=session, skor__isnull=False)
        .values(
            "elemen__kriteria__id",
            "elemen__kriteria__kode",
            "elemen__kriteria__nama",
        )
        .annotate(avg_skor=Avg("skor"))  # rata-rata skor semua elemen dalam kriteria
        .order_by("elemen__kriteria__kode", "elemen__kriteria__nama")
    )

    chart_labels = []
    chart_scores = []
    for k in kriteria_avg:
        kode = k["elemen__kriteria__kode"] or ""
        nama = k["elemen__kriteria__nama"] or ""
        label = f"{nama}" if kode else (nama or "-")
        chart_labels.append(label)
        chart_scores.append(round(k["avg_skor"] or 0, 2))

    # Narasi 
    if chart_scores:
        best_i = max(range(len(chart_scores)), key=lambda i: chart_scores[i])
        worst_i = min(range(len(chart_scores)), key=lambda i: chart_scores[i])
        best_label = chart_labels[best_i]
        worst_label = chart_labels[worst_i]
    else:
        best_label = worst_label = "-"

   # Hitung total elemen dan elemen tanpa dokumen
    total_dokumen_dibutuhkan = 0
    belum_disipakan = 0

    for k in session.program_studi.lembaga_akreditasi.kriteria.all():
        for elemen in k.elemen.all():
         total_dokumen_dibutuhkan += 1
         pd = PenilaianDiri.objects.filter(audit_session=session, elemen=elemen).first()
        if not pd or not pd.bukti_dokumen:  # kalau kosong / NULL
            belum_disipakan += 1

    # hitung persentase
    persen_belum = round((belum_disipakan / total_dokumen_dibutuhkan) * 100, 2) if total_dokumen_dibutuhkan else 0

    #hitung kategori
    # Hitung jumlah temuan per kategori_kondisi
    kategori_counts = (
    audits.values("kategori_kondisi")
          .annotate(jumlah=Count("id"))
          .order_by()
    )

    
    kategori_map = {k["kategori_kondisi"]: k["jumlah"] for k in kategori_counts}



    ctx = {
        "audit_session": session,
        "audits": audits,
        "koordinator_prodi": koordinator_prodi,
        "chart_labels_json": json.dumps(chart_labels),  
        "chart_scores_json": json.dumps(chart_scores),
        "best_label": best_label,
        "worst_label": worst_label,
        "total_dokumen_dibutuhkan": total_dokumen_dibutuhkan,
        "belum_disipakan": belum_disipakan,
        "persen_belum": persen_belum,
        "kategori_map": kategori_map,
    }
    return render(request, "ami/laporan_internal.html", ctx)