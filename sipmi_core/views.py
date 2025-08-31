from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .models import ProgramStudi, Standar, KriteriaED, JadwalED, Auditor, JadwalAMI, PenugasanAuditor
from django.contrib.auth.models import User
from django.contrib import messages
import json

# Helper function to check roles (if using default User)
def is_admin(user):
    return user.is_staff # Simple check, refine if needed

def is_auditor(user):
    # Implement logic based on your user model/roles
    # e.g., return hasattr(user, 'auditor') # if Auditor has a OneToOne link to User
    # For now, placeholder
    return user.groups.filter(name='Auditor').exists()

def is_auditee(user):
    # Implement logic
    return user.groups.filter(name='Auditee').exists()

def is_pimpinan(user):
    # Implement logic
    return user.groups.filter(name='Pimpinan').exists()


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    # Fetch data for dashboard stats (example logic)
    total_prodi = ProgramStudi.objects.count()
    auditor_aktif = Auditor.objects.filter(status='aktif').count()
    # ami_selesai = JadwalAMI.objects.filter(status='selesai').count() # Example
    # progress_ami = calculate_overall_progress() # You'd need a function for this

    context = {
        'total_prodi': total_prodi,
        'auditor_aktif': auditor_aktif,
        # 'ami_selesai': ami_selesai,
        # 'progress_ami': 75, # Placeholder
    }
    return render(request, 'sipmi_core/dashboard.html', context)

# --- Menu: Jadwal Periode ED ---
@login_required
@user_passes_test(is_admin)
def jadwal_ed_list(request):
    jadwal_list = JadwalED.objects.select_related('program_studi').all()
    return render(request, 'sipmi_core/jadwal_ed.html', {'jadwal_list': jadwal_list})

@login_required
@user_passes_test(is_admin)
def jadwal_ed_create(request):
    if request.method == 'POST':
        # Handle form submission (you might want forms.py for this)
        try:
            data = json.loads(request.body)
            prodi_id = data.get('prodi')
            prodi = get_object_or_404(ProgramStudi, pk=prodi_id)
            JadwalED.objects.create(
                program_studi=prodi,
                periode=data['periode'],
                tanggal_mulai=data['tanggal_mulai'],
                tanggal_selesai=data['tanggal_selesai'],
                status=data['status']
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        prodi_list = ProgramStudi.objects.all()
        return render(request, 'sipmi_core/jadwal_ed_form.html', {'prodi_list': prodi_list, 'mode': 'create'})

@login_required
@user_passes_test(is_admin)
def jadwal_ed_update(request, pk):
    jadwal = get_object_or_404(JadwalED, pk=pk)
    if request.method == 'POST':
        try:
             data = json.loads(request.body)
             prodi_id = data.get('prodi')
             prodi = get_object_or_404(ProgramStudi, pk=prodi_id)
             jadwal.program_studi = prodi
             jadwal.periode = data['periode']
             jadwal.tanggal_mulai = data['tanggal_mulai']
             jadwal.tanggal_selesai = data['tanggal_selesai']
             jadwal.status = data['status']
             jadwal.save()
             return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        prodi_list = ProgramStudi.objects.all()
        return render(request, 'sipmi_core/jadwal_ed_form.html', {'jadwal': jadwal, 'prodi_list': prodi_list, 'mode': 'update'})

@login_required
@user_passes_test(is_admin)
def jadwal_ed_delete(request, pk):
    if request.method == 'POST': # Usually DELETE method, but handling via POST for simplicity
        jadwal = get_object_or_404(JadwalED, pk=pk)
        jadwal.delete()
        messages.success(request, 'Jadwal ED berhasil dihapus.')
        return redirect('jadwal_ed_list')
    return JsonResponse({'success': False})


# --- Menu: Kelola Standar ---
@login_required
@user_passes_test(is_admin)
def kelola_standar_list(request):
    standar_list = Standar.objects.all()
    return render(request, 'sipmi_core/kelola_standar.html', {'standar_list': standar_list})

@login_required
@user_passes_test(is_admin)
def standar_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            Standar.objects.create(
                nama=data['nama'],
                deskripsi=data['deskripsi']
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_admin)
def standar_update(request, pk):
    standar = get_object_or_404(Standar, pk=pk)
    if request.method == 'POST':
        try:
             data = json.loads(request.body)
             standar.nama = data['nama']
             standar.deskripsi = data['deskripsi']
             standar.save()
             return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_admin)
def standar_delete(request, pk):
    if request.method == 'POST':
        standar = get_object_or_404(Standar, pk=pk)
        standar.delete()
        messages.success(request, 'Standar berhasil dihapus.')
        return redirect('kelola_standar_list')
    return JsonResponse({'success': False})


# --- Menu: Form Kriteria ED ---
@login_required
@user_passes_test(is_admin)
def form_kriteria_list(request):
    kriteria_list = KriteriaED.objects.select_related('standar').all()
    standar_list = Standar.objects.all()
    return render(request, 'sipmi_core/form_kriteria.html', {'kriteria_list': kriteria_list, 'standar_list': standar_list})

@login_required
@user_passes_test(is_admin)
def kriteria_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            standar_id = data.get('standar')
            standar = get_object_or_404(Standar, pk=standar_id)
            KriteriaED.objects.create(
                standar=standar,
                nama=data['nama'],
                bobot=data['bobot'],
                status=data['status']
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_admin)
def kriteria_update(request, pk):
    kriteria = get_object_or_404(KriteriaED, pk=pk)
    if request.method == 'POST':
        try:
             data = json.loads(request.body)
             standar_id = data.get('standar')
             standar = get_object_or_404(Standar, pk=standar_id)
             kriteria.standar = standar
             kriteria.nama = data['nama']
             kriteria.bobot = data['bobot']
             kriteria.status = data['status']
             kriteria.save()
             return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_admin)
def kriteria_delete(request, pk):
    if request.method == 'POST':
        kriteria = get_object_or_404(KriteriaED, pk=pk)
        kriteria.delete()
        messages.success(request, 'Kriteria berhasil dihapus.')
        return redirect('form_kriteria_list')
    return JsonResponse({'success': False})


# --- Menu: Lihat Progress ---
@login_required
def lihat_progress(request):
    # This needs more complex logic to fetch actual progress data
    # Placeholder data for now, similar to the frontend JS
    progress_ed_data = [
        {'prodi': 'Teknik Informatika', 'progress': 100},
        {'prodi': 'Ekonomi Pembangunan', 'progress': 75},
        # ... fetch from DB ...
    ]
    progress_ami_data = [
        {'prodi': 'Teknik Informatika', 'progress': 100},
        {'prodi': 'Ekonomi Pembangunan', 'progress': 30},
        # ... fetch from DB ...
    ]
    return render(request, 'sipmi_core/lihat_progress.html', {'progress_ed_data': progress_ed_data, 'progress_ami_data': progress_ami_data})


# --- Menu: Jadwal AMI ---
@login_required
@user_passes_test(is_admin)
def jadwal_ami_list(request):
    jadwal_list = JadwalAMI.objects.select_related('program_studi', 'auditor').all()
    return render(request, 'sipmi_core/jadwal_ami.html', {'jadwal_list': jadwal_list})

@login_required
@user_passes_test(is_admin)
def ami_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prodi_id = data.get('prodi')
            auditor_id = data.get('auditor')
            prodi = get_object_or_404(ProgramStudi, pk=prodi_id)
            auditor = get_object_or_404(Auditor, pk=auditor_id)
            JadwalAMI.objects.create(
                program_studi=prodi,
                auditor=auditor,
                tanggal=data['tanggal'],
                status=data['status']
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        prodi_list = ProgramStudi.objects.all()
        auditor_list = Auditor.objects.filter(status='aktif') # Only active auditors
        return render(request, 'sipmi_core/jadwal_ami_form.html', {'prodi_list': prodi_list, 'auditor_list': auditor_list, 'mode': 'create'})

@login_required
@user_passes_test(is_admin)
def ami_update(request, pk):
    jadwal = get_object_or_404(JadwalAMI, pk=pk)
    if request.method == 'POST':
        try:
             data = json.loads(request.body)
             prodi_id = data.get('prodi')
             auditor_id = data.get('auditor')
             prodi = get_object_or_404(ProgramStudi, pk=prodi_id)
             auditor = get_object_or_404(Auditor, pk=auditor_id)
             jadwal.program_studi = prodi
             jadwal.auditor = auditor
             jadwal.tanggal = data['tanggal']
             jadwal.status = data['status']
             jadwal.save()
             return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        prodi_list = ProgramStudi.objects.all()
        auditor_list = Auditor.objects.filter(status='aktif')
        return render(request, 'sipmi_core/jadwal_ami_form.html', {'jadwal': jadwal, 'prodi_list': prodi_list, 'auditor_list': auditor_list, 'mode': 'update'})

@login_required
@user_passes_test(is_admin)
def ami_delete(request, pk):
    if request.method == 'POST':
        jadwal = get_object_or_404(JadwalAMI, pk=pk)
        jadwal.delete()
        messages.success(request, 'Jadwal AMI berhasil dihapus.')
        return redirect('jadwal_ami_list')
    return JsonResponse({'success': False})


# --- Menu: Penugasan Auditor ---
@login_required
@user_passes_test(is_admin)
def penugasan_auditor_list(request):
    penugasan_list = PenugasanAuditor.objects.select_related('auditor', 'program_studi').all()
    return render(request, 'sipmi_core/penugasan_auditor.html', {'penugasan_list': penugasan_list})

@login_required
@user_passes_test(is_admin)
def penugasan_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            auditor_id = data.get('auditor')
            prodi_id = data.get('prodi')
            auditor = get_object_or_404(Auditor, pk=auditor_id)
            prodi = get_object_or_404(ProgramStudi, pk=prodi_id)
            PenugasanAuditor.objects.create(
                auditor=auditor,
                program_studi=prodi,
                periode=data['periode'],
                status=data['status']
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        auditor_list = Auditor.objects.filter(status='aktif')
        prodi_list = ProgramStudi.objects.all()
        return render(request, 'sipmi_core/penugasan_form.html', {'auditor_list': auditor_list, 'prodi_list': prodi_list, 'mode': 'create'})

@login_required
@user_passes_test(is_admin)
def penugasan_update(request, pk):
    penugasan = get_object_or_404(PenugasanAuditor, pk=pk)
    if request.method == 'POST':
       try:
             data = json.loads(request.body)
             auditor_id = data.get('auditor')
             prodi_id = data.get('prodi')
             auditor = get_object_or_404(Auditor, pk=auditor_id)
             prodi = get_object_or_404(ProgramStudi, pk=prodi_id)
             penugasan.auditor = auditor
             penugasan.program_studi = prodi
             penugasan.periode = data['periode']
             penugasan.status = data['status']
             penugasan.save()
             return JsonResponse({'success': True})
       except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        auditor_list = Auditor.objects.filter(status='aktif')
        prodi_list = ProgramStudi.objects.all()
        return render(request, 'sipmi_core/penugasan_form.html', {'penugasan': penugasan, 'auditor_list': auditor_list, 'prodi_list': prodi_list, 'mode': 'update'})

@login_required
@user_passes_test(is_admin)
def penugasan_delete(request, pk):
    if request.method == 'POST':
        penugasan = get_object_or_404(PenugasanAuditor, pk=pk)
        penugasan.delete()
        messages.success(request, 'Penugasan berhasil dihapus.')
        return redirect('penugasan_auditor_list')
    return JsonResponse({'success': False})


# --- Menu: Kelola Auditor ---
@login_required
@user_passes_test(is_admin)
def kelola_auditor_list(request):
    auditor_list = Auditor.objects.select_related('user').all()
    return render(request, 'sipmi_core/kelola_auditor.html', {'auditor_list': auditor_list})

@login_required
@user_passes_test(is_admin)
def auditor_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Create User first (simplified, add password/email handling)
            user = User.objects.create_user(username=data['username'], email=data.get('email', ''), password=data['password'])
            Auditor.objects.create(
                user=user,
                nip=data.get('nip', ''),
                jabatan=data.get('jabatan', ''),
                sertifikat_status=data['sertifikat_status'],
                status=data['status']
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return render(request, 'sipmi_core/auditor_form.html', {'mode': 'create'})

@login_required
@user_passes_test(is_admin)
def auditor_update(request, pk):
    auditor = get_object_or_404(Auditor, pk=pk)
    if request.method == 'POST':
        try:
             data = json.loads(request.body)
             auditor.user.username = data['username']
             # Handle email/password updates carefully
             # auditor.user.email = data.get('email', '')
             auditor.user.save()
             auditor.nip = data.get('nip', '')
             auditor.jabatan = data.get('jabatan', '')
             auditor.sertifikat_status = data['sertifikat_status']
             auditor.status = data['status']
             auditor.save()
             return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return render(request, 'sipmi_core/auditor_form.html', {'auditor': auditor, 'mode': 'update'})

@login_required
@user_passes_test(is_admin)
def auditor_delete(request, pk):
    if request.method == 'POST':
        auditor = get_object_or_404(Auditor, pk=pk)
        # Consider deleting the associated User or deactivating
        auditor.user.is_active = False
        auditor.user.save()
        # auditor.delete() # Or delete if preferred
        messages.success(request, 'Auditor berhasil dihapus (dinonaktifkan).')
        return redirect('kelola_auditor_list')
    return JsonResponse({'success': False})


# --- Menu: Kelola Auditi (Prodi) ---
@login_required
@user_passes_test(is_admin)
def kelola_auditi_list(request):
    auditi_list = ProgramStudi.objects.all() # Assuming Auditi is Prodi for now
    return render(request, 'sipmi_core/kelola_auditi.html', {'auditi_list': auditi_list})

@login_required
@user_passes_test(is_admin)
def auditi_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ProgramStudi.objects.create(
                nama=data['nama'],
                # Add other fields like Fakultas, Kaprodi link if needed
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return render(request, 'sipmi_core/auditi_form.html', {'mode': 'create'})

@login_required
@user_passes_test(is_admin)
def auditi_update(request, pk):
    auditi = get_object_or_404(ProgramStudi, pk=pk) # Assuming Auditi is Prodi
    if request.method == 'POST':
        try:
             data = json.loads(request.body)
             auditi.nama = data['nama']
             # Update other fields
             auditi.save()
             return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return render(request, 'sipmi_core/auditi_form.html', {'auditi': auditi, 'mode': 'update'})

@login_required
@user_passes_test(is_admin)
def auditi_delete(request, pk):
    if request.method == 'POST':
        auditi = get_object_or_404(ProgramStudi, pk=pk) # Assuming Auditi is Prodi
        auditi.delete()
        messages.success(request, 'Auditi berhasil dihapus.')
        return redirect('kelola_auditi_list')
    return JsonResponse({'success': False})

# --- Menu: Kelola Password User ---
# This is usually handled by Django's built-in views or custom admin actions.
# For simplicity, redirecting to Django admin or a placeholder.
@login_required
@user_passes_test(is_admin)
def kelola_password(request):
    # messages.info(request, 'Gunakan Django Admin untuk mengelola password pengguna.')
    # return redirect('admin:index') # Redirect to Django Admin
    # Or create a simple list view if needed
    users = User.objects.all()
    return render(request, 'sipmi_core/kelola_password.html', {'users': users})

# Add specific password reset view if needed (using Django's auth views is recommended)
# from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
# Then add URLs for these views
