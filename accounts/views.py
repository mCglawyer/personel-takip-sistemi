# accounts/views.py (En Güncel ve Tam Hali - QR Tarayıcı Dahil - 23 Ekim 2025)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
# Yetkilendirme için user_passes_test
from django.contrib.auth.decorators import login_required, user_passes_test
# Şifre değiştirme formu
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from datetime import datetime, timedelta, date # Gerekli tüm datetime modülleri
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User # User modelini import ediyoruz
from django.contrib import messages # Başarı/Uyarı mesajları için
import calendar # Aylık puantaj raporu için
import json # FullCalendar için JSON işlemleri
from django.core.mail import send_mail # E-posta göndermek için
from django.conf import settings # settings.py'daki e-posta ayarlarını almak için

# Modellerimizi ve vardiya tipleri listesini models.py'dan import ediyoruz
from .models import Branch, Break, Shift, SHIFT_TYPES, Profile, LeaveRequest
# Formlarımızı forms.py'dan import ediyoruz
from .forms import PersonnelAddForm, LeaveRequestForm

# --------------------------------------------------------------------------
# Yardımcı Fonksiyonlar (Yetki Kontrolü)
# --------------------------------------------------------------------------

def is_manager_or_superuser(user):
    """Kullanıcının superuser olup olmadığını VEYA yetkili planlama gruplarından
       (Şube Şefi, Bölge Yöneticisi) birine üye olup olmadığını kontrol eder."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name__in=['Şube Şefi', 'Bölge Yöneticisi']).exists()

def is_report_viewer_or_superuser(user):
    """Kullanıcının superuser olup olmadığını VEYA rapor görme yetkili grubuna
       ('Bölge Yöneticisi') üye olup olmadığını kontrol eder."""
    if not user.is_authenticated:
        return False
    # Raporları sadece superuser VEYA Bölge Yöneticisi görebilir
    return user.is_superuser or user.groups.filter(name='Bölge Yöneticisi').exists()

# --------------------------------------------------------------------------
# Kimlik Doğrulama (Authentication)
# --------------------------------------------------------------------------

def login_view(request):
    """Kullanıcı giriş ekranını yönetir."""
    error_message = None
    if request.user.is_authenticated:
        return redirect('accounts:dashboard') # Namespace ('accounts:') eklendi

    if request.method == 'POST':
        username_data = request.POST.get('username')
        password_data = request.POST.get('password')
        user = authenticate(request, username=username_data, password=password_data)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard') # Namespace ('accounts:') eklendi
        else:
            error_message = "Kullanıcı adı veya şifre hatalı."

    context = {'error_message': error_message}
    return render(request, 'index.html', context)

def logout_view(request):
    """Kullanıcının oturumunu sonlandırır ve giriş ekranına yönlendirir."""
    logout(request)
    messages.info(request, "Başarıyla çıkış yaptınız.")
    return redirect('login') # Giriş sayfası ana URL'de olduğu için namespace yok

# --------------------------------------------------------------------------
# Ana Panel / Dashboard (Yönetici ve Personel Ayrımı)
# --------------------------------------------------------------------------

@login_required(login_url='login')
def dashboard_view(request):
    """Giriş yapan kullanıcının yönetici mi (admin/şef/bölge) yoksa
       normal personel mi olduğuna göre farklı içerik gösterir."""
    context = {'user': request.user}

    # Yetki kontrolü (Planlama yetkisi olanlar yönetici panelini görür)
    if is_manager_or_superuser(request.user):
        # --- YÖNETİCİ GÖRÜNÜMÜ ---
        # Rolüne göre mola listesini filtrele:
        if is_report_viewer_or_superuser(request.user): # Superuser veya Bölge Yön.
            all_breaks = Break.objects.all().order_by('-start_time').select_related('personnel', 'branch')
            report_title = "Genel Mola Takip Raporu (Tüm Şubeler)"
        else: # Sadece Şube Şefi ise
            try:
                manager_branch = request.user.profile.branch
                if manager_branch:
                    all_breaks = Break.objects.filter(branch=manager_branch).order_by('-start_time').select_related('personnel', 'branch')
                    report_title = f"{manager_branch.name} Şubesi Mola Takip Raporu"
                else:
                    all_breaks = Break.objects.none()
                    report_title = "Genel Mola Takip Raporu (Şube Atanmamış)"
                    messages.warning(request, "Size atanmış bir şube bulunamadı.")
            except Profile.DoesNotExist:
                 all_breaks = Break.objects.none()
                 report_title = "Genel Mola Takip Raporu (Profil Bulunamadı)"
                 messages.error(request, "Profil bilgileriniz bulunamadı.")

        active_breaks_count = all_breaks.filter(end_time=None).count()

        context.update({
            'is_admin': True, # Template bu değişkene göre davranıyor
            'all_breaks_list': all_breaks,
            'active_breaks_count': active_breaks_count,
            'report_title': report_title
        })
        return render(request, 'dashboard.html', context)

    else:
        # --- NORMAL PERSONEL GÖRÜNÜMÜ ---
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        personnel_shifts = Shift.objects.filter(
            personnel=request.user, date__gte=start_of_week, date__lte=end_of_week
        ).order_by('date').select_related('branch')

        active_break = Break.objects.filter(
            personnel=request.user, end_time=None
        ).select_related('branch').first()

        # FullCalendar için Vardiya Verisini JSON Formatına Çevir
        calendar_events = []
        for shift in personnel_shifts:
            event_title = shift.get_shift_type_display()
            event_color, border_color, text_color = '', '#ccc', '#333' # Varsayılanlar
            if shift.shift_type == 'SABAH':   event_color, border_color = '#e6f7ff', '#91d5ff'
            elif shift.shift_type == 'ARACI': event_color, border_color = '#fffbe6', '#ffe58f'
            elif shift.shift_type == 'AKSAM': event_color, border_color = '#fff0f6', '#ffadd2'
            elif shift.shift_type == 'IZIN':    event_title, event_color, border_color, text_color = "İzinli", '#f6f6f6', '#d9d9d9', '#555'
            elif shift.shift_type == 'RAPORLU': event_title, event_color, border_color, text_color = "Raporlu", '#fff3cd', '#ffeeba', '#856404'
            elif shift.shift_type == 'DEVAMSIZ':event_title, event_color, border_color, text_color = "Devamsız", '#f8d7da', '#f5c6cb', '#721c24'
            elif shift.shift_type == 'ETKINLIK':
                 event_color, border_color = '#f9f0ff', '#d3adf7'
                 if shift.start_time and shift.end_time:
                     event_title = f"Etkinlik ({shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M')})"

            calendar_event = {
                'title': event_title, 'start': shift.date.strftime('%Y-%m-%d'),
                'allDay': True, 'backgroundColor': event_color,
                'borderColor': border_color, 'textColor': text_color
            }
            if shift.branch:
                calendar_event['extendedProps'] = {'branch': shift.branch.name}
            calendar_events.append(calendar_event)

        context.update({
            'is_admin': False, # Yönetici değil
            'calendar_events_json': json.dumps(calendar_events), # JSON takvim verisi
            'active_break': active_break,
            'today': today,
            'start_of_week': start_of_week,
            'end_of_week': end_of_week,
        })
        return render(request, 'dashboard.html', context)

# --------------------------------------------------------------------------
# Profil Sayfası ve Şifre Değiştirme
# --------------------------------------------------------------------------
@login_required(login_url='login')
def profile_view(request):
    """Kullanıcının profil bilgilerini gösterir ve şifre değiştirmesine olanak tanır."""
    user = request.user
    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST' and 'change_password' in request.POST:
        password_form = PasswordChangeForm(user=user, data=request.POST)
        if password_form.is_valid():
            updated_user = password_form.save()
            update_session_auth_hash(request, updated_user) # Oturumu güncel tut
            messages.success(request, 'Şifreniz başarıyla güncellendi!')
            return redirect('accounts:profile') # Aynı sayfaya geri dön
        else:
            messages.error(request, 'Şifre değiştirilemedi. Lütfen hataları kontrol edin.')

    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = None # Profil yoksa (olmamalı)

    context = { 'user': user, 'profile': profile, 'password_form': password_form }
    return render(request, 'profile.html', context)

# --------------------------------------------------------------------------
# Mola İşlemleri
# --------------------------------------------------------------------------

@login_required(login_url='login')
def toggle_break_view(request, branch_id):
    """QR kod okutulduğunda personelin molasını başlatır veya bitirir."""
    personnel = request.user
    branch = get_object_or_404(Branch, id=branch_id)
    active_break = Break.objects.filter(personnel=personnel, end_time=None).first()
    message = ""
    if active_break is None:
        Break.objects.create(personnel=personnel, branch=branch)
        message = "Mola başarıyla başlatıldı."
    else:
        active_break.end_time = timezone.now()
        active_break.save()
        message = "Mola başarıyla bitirildi."
    context = { 'message': message, 'branch': branch }
    return render(request, 'mola_onay.html', context)

@login_required(login_url='login')
@user_passes_test(is_report_viewer_or_superuser, login_url='accounts:dashboard')
def exceeded_breaks_report_view(request):
    """Günlük toplam mola süresi (örn: 63 dk) aşan personelleri listeler."""
    completed_breaks = Break.objects.filter(end_time__isnull=False)
    breaks_with_duration = completed_breaks.annotate(duration=ExpressionWrapper( F('end_time') - F('start_time'), output_field=DurationField() ))
    daily_break_totals = breaks_with_duration.annotate(date=TruncDate('start_time')).values('personnel__username', 'date').annotate(total_duration=Sum('duration')).order_by('-date', 'personnel__username')
    limit_minutes = 63
    limit = timedelta(minutes=limit_minutes)
    exceeded_list = daily_break_totals.filter(total_duration__gt=limit)
    context = {'user': request.user, 'exceeded_list': exceeded_list, 'limit_minutes': limit_minutes}
    return render(request, 'exceeded_report.html', context)

# --------------------------------------------------------------------------
# Haftalık Vardiya Planlama (Yöneticiler İçin)
# --------------------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_manager_or_superuser, login_url='accounts:dashboard')
def weekly_schedule_select_view(request):
    """Yöneticinin hangi şube için planlama yapmak istediğini seçtiği sayfa."""
    branches = Branch.objects.all().order_by('name')
    context = {'user': request.user, 'branches': branches}
    return render(request, 'weekly_schedule_select.html', context)

@login_required(login_url='login')
@user_passes_test(is_manager_or_superuser, login_url='accounts:dashboard')
def weekly_schedule_view(request, branch_id):
    """Seçilen şube için haftalık vardiya planlama tablosunu gösterir ve kaydeder."""
    branch = get_object_or_404(Branch, id=branch_id)
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    week_days = [start_of_week + timedelta(days=i) for i in range(7)]
    personnel_in_branch = User.objects.filter(is_superuser=False, profile__branch=branch, is_active=True).order_by('username').select_related('profile')
    if request.method == 'POST':
        for p in personnel_in_branch:
            branch_obj = branch
            for day in week_days:
                day_str = day.strftime('%Y-%m-%d'); select_name = f"shift_{p.id}_{day_str}"
                shift_type = request.POST.get(select_name)
                if shift_type: Shift.objects.update_or_create(personnel=p, date=day, defaults={'shift_type': shift_type, 'branch': branch_obj})
                else: Shift.objects.filter(personnel=p, date=day).delete()
        messages.success(request, f'{branch.name} şubesi için haftalık plan başarıyla kaydedildi!')
        return redirect('accounts:weekly_schedule_branch', branch_id=branch.id)
    existing_shifts = Shift.objects.filter(personnel__in=personnel_in_branch, date__gte=start_of_week, date__lte=week_days[6]).select_related('personnel', 'branch')
    shifts_map = {};
    for shift in existing_shifts: p_id_str=str(shift.personnel.id); day_str=shift.date.strftime('%Y-%m-%d'); shifts_map.setdefault(p_id_str, {})[day_str]=shift
    context = {'user': request.user, 'selected_branch': branch, 'week_days': week_days, 'all_personnel': personnel_in_branch, 'shift_types': SHIFT_TYPES, 'shifts_map': shifts_map}
    return render(request, 'weekly_schedule.html', context)

# --------------------------------------------------------------------------
# Haftalık Mola Raporları (Sadece Rapor Yetkisi Olanlar)
# --------------------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_report_viewer_or_superuser, login_url='accounts:dashboard')
def break_report_select_view(request):
    """Yöneticinin hangi şubenin haftalık mola raporunu görmek istediğini seçtiği sayfa."""
    branches = Branch.objects.all().order_by('name')
    context = {'user': request.user, 'branches': branches}
    return render(request, 'break_report_select.html', context)

@login_required(login_url='login')
@user_passes_test(is_report_viewer_or_superuser, login_url='accounts:dashboard')
def break_report_weekly_view(request, branch_id):
    """Seçilen şubenin ilgili haftadaki tüm mola kayıtlarını listeler."""
    branch = get_object_or_404(Branch, id=branch_id)
    today = timezone.now().date(); start_of_week = today - timedelta(days=today.weekday()); end_of_week = start_of_week + timedelta(days=6)
    weekly_breaks = Break.objects.filter(branch=branch, start_time__date__gte=start_of_week, start_time__date__lte=end_of_week).select_related('personnel').order_by('start_time')
    context = {'user': request.user, 'selected_branch': branch, 'start_of_week': start_of_week, 'end_of_week': end_of_week, 'weekly_breaks_list': weekly_breaks}
    return render(request, 'break_report_weekly.html', context)

# --------------------------------------------------------------------------
# Aylık Puantaj Raporları (Sadece Rapor Yetkisi Olanlar)
# --------------------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_report_viewer_or_superuser, login_url='accounts:dashboard')
def attendance_report_select_view(request):
    """Yöneticinin hangi şube ve ay için puantaj raporu istediğini seçtiği sayfa."""
    branches = Branch.objects.all().order_by('name')
    current_year = timezone.now().year; years = range(current_year - 1, current_year + 2); months = range(1, 13)
    if request.method == 'GET' and all(k in request.GET for k in ('branch', 'year', 'month')):
        selected_branch_id = request.GET.get('branch'); selected_year = request.GET.get('year'); selected_month = request.GET.get('month')
        if selected_branch_id and selected_year and selected_month:
            try: return redirect('accounts:attendance_report_monthly', branch_id=int(selected_branch_id), year=int(selected_year), month=int(selected_month))
            except (ValueError, TypeError): messages.error(request, "Lütfen geçerli bir şube, yıl ve ay seçin.")
    context = {'user': request.user, 'branches': branches, 'years': years, 'months': months, 'current_year': current_year, 'current_month': timezone.now().month}
    return render(request, 'attendance_report_select.html', context)

@login_required(login_url='login')
@user_passes_test(is_report_viewer_or_superuser, login_url='accounts:dashboard')
def attendance_report_monthly_view(request, branch_id, year, month):
    """Seçilen şube ve ay için personel bazında devamlılık özetini gösterir (İzin/Rapor ayrı)."""
    branch = get_object_or_404(Branch, id=branch_id)
    try: start_date = date(year, month, 1); num_days = calendar.monthrange(year, month)[1]; end_date = date(year, month, num_days)
    except ValueError: messages.error(request, "Geçersiz tarih seçimi."); return redirect('accounts:attendance_report_select')
    personnel_in_branch = User.objects.filter(is_superuser=False, profile__branch=branch, is_active=True).order_by('username').select_related('profile')
    shifts_in_month = Shift.objects.filter(personnel__in=personnel_in_branch, date__gte=start_date, date__lte=end_date).select_related('personnel')
    shifts_map = {};
    for shift in shifts_in_month: p_id = shift.personnel.id; day_date = shift.date; shifts_map.setdefault(p_id, {})[day_date] = shift.shift_type
    report_data = []; days_in_month = [start_date + timedelta(days=i) for i in range(num_days)]
    work_types = ['SABAH', 'ARACI', 'AKSAM', 'ETKINLIK']; unexcused_types = ['DEVAMSIZ']
    for p in personnel_in_branch:
        p_id = p.id; counts = {'worked': 0, 'leave': 0, 'reported': 0, 'unexcused': 0, 'off': 0}
        for day_date in days_in_month:
            shift_type = shifts_map.get(p_id, {}).get(day_date)
            if shift_type in work_types: counts['worked'] += 1
            elif shift_type == 'IZIN': counts['leave'] += 1
            elif shift_type == 'RAPORLU': counts['reported'] += 1
            elif shift_type in unexcused_types: counts['unexcused'] += 1
            else: counts['off'] += 1
        report_data.append({'personnel': p, 'counts': counts, 'total_days': num_days})
    context = {'user': request.user, 'selected_branch': branch, 'selected_year': year, 'selected_month': month, 'start_date': start_date, 'end_date': end_date, 'report_data': report_data}
    return render(request, 'attendance_report_monthly.html', context)

# --------------------------------------------------------------------------
# Personel Yönetimi (Yöneticiler İçin)
# --------------------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_manager_or_superuser, login_url='accounts:dashboard')
def personnel_list_view(request):
    """Personel listesini (aktif ve dondurulmuş) gösterir."""
    personnel_list = User.objects.filter(is_superuser=False).select_related('profile', 'profile__branch').order_by('username')
    context = {'user': request.user, 'personnel_list': personnel_list}
    return render(request, 'personnel_list.html', context)

@login_required(login_url='login')
@user_passes_test(is_manager_or_superuser, login_url='accounts:dashboard')
def personnel_add_view(request):
    """Yeni personel ekleme formunu gösterir ve işler."""
    if request.method == 'POST':
        form = PersonnelAddForm(request.POST)
        if form.is_valid():
            new_user = form.save(); selected_branch = form.cleaned_data['branch']
            Profile.objects.update_or_create(user=new_user, defaults={'branch': selected_branch})
            messages.success(request, f'Personel "{new_user.username}" başarıyla eklendi ve {selected_branch.name} şubesine atandı.')
            return redirect('accounts:personnel_list')
        else: messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else: form = PersonnelAddForm()
    context = {'user': request.user, 'form': form}
    return render(request, 'personnel_add.html', context)

@login_required(login_url='login')
@user_passes_test(is_manager_or_superuser, login_url='accounts:dashboard')
def personnel_deactivate_view(request, user_id):
    """Bir personelin hesabını dondurur."""
    target_user = get_object_or_404(User, id=user_id)
    if target_user.is_superuser or target_user == request.user: messages.error(request, "Bu hesap dondurulamaz."); return redirect('accounts:personnel_list')
    if request.method == 'POST': target_user.is_active = False; target_user.save(); messages.warning(request, f'Personel "{target_user.username}" hesabı donduruldu.')
    else: messages.warning(request, "Geçersiz istek.")
    return redirect('accounts:personnel_list')

@login_required(login_url='login')
@user_passes_test(is_manager_or_superuser, login_url='accounts:dashboard')
def personnel_activate_view(request, user_id):
    """Dondurulmuş bir personel hesabını aktifleştirir."""
    target_user = get_object_or_404(User, id=user_id, is_active=False) # Sadece aktif olmayanlar
    if target_user == request.user: return redirect('accounts:personnel_list') # Kendini aktive edemez
    if request.method == 'POST': target_user.is_active = True; target_user.save(); messages.success(request, f'Personel "{target_user.username}" hesabı tekrar aktifleştirildi.')
    else: messages.warning(request, "Geçersiz istek.")
    return redirect('accounts:personnel_list')

# --------------------------------------------------------------------------
# İzin/Rapor Talepleri (Personel + Yönetici)
# --------------------------------------------------------------------------

@login_required(login_url='login')
def leave_request_create_view(request):
    """Personelin yeni izin/Rapor talebi oluşturma formunu gösterir ve işler."""
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.personnel = request.user
            leave_request.save()
            messages.success(request, 'Talebiniz başarıyla oluşturuldu ve onaya gönderildi.')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Talep oluşturulamadı. Lütfen formdaki hataları kontrol edin.')
    else:
        form = LeaveRequestForm()
    context = {'user': request.user, 'form': form}
    return render(request, 'leave_request_form.html', context)

@login_required(login_url='login')
def my_leave_requests_view(request):
    """Giriş yapmış personelin kendi izin/Rapor taleplerini listeler."""
    user = request.user
    my_requests = LeaveRequest.objects.filter(personnel=user).order_by('-created_at').select_related('processed_by') # İşleyeni de al
    context = {'user': user, 'my_requests': my_requests}
    return render(request, 'my_leave_requests.html', context)

@login_required(login_url='login')
@user_passes_test(is_manager_or_superuser, login_url='accounts:dashboard')
def pending_leave_requests_view(request):
    """Yöneticinin rolüne göre filtrelenmiş onay bekleyen izin/Rapor taleplerini listeler."""
    user = request.user
    pending_requests_query = LeaveRequest.objects.filter(status='BEKLIYOR').select_related(
        'personnel', 'personnel__profile__branch'
    ).order_by('start_date')

    # Yetkiye göre filtrele
    if is_report_viewer_or_superuser(user): # Superuser veya Bölge Yön.
        final_pending_requests = pending_requests_query
        view_title = "Bekleyen İzin/Rapor Talepleri (Tüm Şubeler)"
    elif user.groups.filter(name='Şube Şefi').exists(): # Sadece Şube Şefi
        try:
            manager_branch = user.profile.branch
            if manager_branch:
                final_pending_requests = pending_requests_query.filter(personnel__profile__branch=manager_branch)
                view_title = f"{manager_branch.name} Şubesi Bekleyen Talepler"
            else:
                messages.warning(request, "Size atanmış bir şube olmadığı için talep göremiyorsunuz.")
                final_pending_requests = LeaveRequest.objects.none()
                view_title = "Bekleyen İzin/Rapor Talepleri (Şube Atanmamış)"
        except Profile.DoesNotExist:
             messages.error(request, "Profil bilgileriniz bulunamadı.")
             final_pending_requests = LeaveRequest.objects.none()
             view_title = "Bekleyen İzin/Rapor Talepleri (Profil Hatası)"
    else: # Buraya düşmemeli
         final_pending_requests = LeaveRequest.objects.none()
         view_title = "Bekleyen İzin/Rapor Talepleri (Yetki Yok)"

    context = {'user': user, 'pending_requests': final_pending_requests, 'view_title': view_title}
    return render(request, 'pending_leave_requests.html', context)

@login_required(login_url='login')
@user_passes_test(is_manager_or_superuser, login_url='accounts:dashboard')
def process_leave_request_view(request, request_id):
    """Yöneticinin belirli bir izin/Rapor talebini onaylamasını veya reddetmesini sağlar."""
    leave_request = get_object_or_404(LeaveRequest.objects.select_related('personnel__profile'), id=request_id, status='BEKLIYOR') # Profil bilgisini de çekelim
    user = request.user

    # Yetki Kontrolü: Şube Şefi sadece kendi şubesini işleyebilir
    if not is_report_viewer_or_superuser(user) and user.groups.filter(name='Şube Şefi').exists():
        try:
            manager_branch = user.profile.branch
            if not manager_branch or not hasattr(leave_request.personnel, 'profile') or leave_request.personnel.profile.branch != manager_branch:
                messages.error(request, "Bu talebi işleme yetkiniz yok (Farklı Şube veya Profil Eksik).")
                return redirect('accounts:pending_leave_requests')
        except Profile.DoesNotExist:
             messages.error(request, "Profil veya talep eden kişinin profili bulunamadı.")
             return redirect('accounts:pending_leave_requests')

    if request.method == 'POST':
        action = request.POST.get('action')
        manager_notes = request.POST.get('manager_notes', '')

        if action == 'approve':
            # --- ONAYLAMA ---
            leave_request.status = 'ONAYLANDI'; leave_request.processed_by = user; leave_request.processed_at = timezone.now()
            leave_request.manager_notes = manager_notes; leave_request.save()

            # --- VARDİYA GÜNCELLEME ---
            current_date = leave_request.start_date
            shift_type_map = {'IZIN': 'IZIN', 'RAPOR': 'RAPORLU'}
            resulting_shift_type = shift_type_map.get(leave_request.request_type, 'IZIN')
            personnel_branch = leave_request.personnel.profile.branch if hasattr(leave_request.personnel, 'profile') else None
            while current_date <= leave_request.end_date:
                Shift.objects.update_or_create(personnel=leave_request.personnel, date=current_date, defaults={'shift_type': resulting_shift_type, 'branch': personnel_branch})
                current_date += timedelta(days=1)
            messages.success(request, f"{leave_request.personnel.username} için {leave_request.get_request_type_display()} talebi onaylandı ve vardiya planına işlendi.")

            # --- E-POSTA GÖNDER (ONAY) ---
            recipient_email = leave_request.personnel.email
            if recipient_email:
                email_subject = f"İzin/Rapor Talebiniz Onaylandı ({leave_request.start_date.strftime('%d.%m')} - {leave_request.end_date.strftime('%d.%m')})"
                email_message = f"Merhaba {leave_request.personnel.first_name or leave_request.personnel.username},\n\n{leave_request.start_date.strftime('%d.%m.%Y')} - {leave_request.end_date.strftime('%d.%m.%Y')} tarihleri arasındaki '{leave_request.get_request_type_display()}' talebiniz onaylanmıştır.\n\nYönetici Notu:\n{manager_notes or '(Not eklenmedi)'}\n\nİlgili günler vardiya planınıza işlenmiştir.\n\nİyi çalışmalar."
                try: send_mail(email_subject, email_message, settings.DEFAULT_FROM_EMAIL, [recipient_email], fail_silently=False)
                except Exception as e: print(f"Onay e-postası gönderirken hata: {e}"); messages.error(request, f"Talep onaylandı ancak personele ({recipient_email}) bildirim e-postası gönderilemedi.")

        elif action == 'reject':
            # --- REDDETME ---
            leave_request.status = 'REDDEDILDI'; leave_request.processed_by = user; leave_request.processed_at = timezone.now()
            leave_request.manager_notes = manager_notes; leave_request.save()
            messages.warning(request, f"{leave_request.personnel.username} için {leave_request.get_request_type_display()} talebi reddedildi.")

            # --- E-POSTA GÖNDER (RED) ---
            recipient_email = leave_request.personnel.email
            if recipient_email:
                email_subject = f"İzin/Rapor Talebiniz Reddedildi ({leave_request.start_date.strftime('%d.%m')} - {leave_request.end_date.strftime('%d.%m')})"
                email_message = f"Merhaba {leave_request.personnel.first_name or leave_request.personnel.username},\n\n{leave_request.start_date.strftime('%d.%m.%Y')} - {leave_request.end_date.strftime('%d.%m.%Y')} tarihleri arasındaki '{leave_request.get_request_type_display()}' talebiniz maalesef reddedilmiştir.\n\nYönetici Notu:\n{manager_notes or '(Not eklenmedi)'}\n\nDetaylı bilgi için yöneticinizle görüşebilirsiniz.\n\nİyi çalışmalar."
                try: send_mail(email_subject, email_message, settings.DEFAULT_FROM_EMAIL, [recipient_email], fail_silently=False)
                except Exception as e: print(f"Red e-postası gönderirken hata: {e}"); messages.error(request, f"Talep reddedildi ancak personele ({recipient_email}) bildirim e-postası gönderilemedi.")

        else:
            messages.error(request, "Geçersiz işlem.")
        return redirect('accounts:pending_leave_requests') # Listeye geri dön
    else: # GET isteği ise
        messages.warning(request, "Geçersiz istek yöntemi.")
        return redirect('accounts:pending_leave_requests') # Listeye yönlendir


# --------------------------------------------------------------------------
# QR Kod Tarayıcı (Personel İçin) - DÜZELTİLMİŞ GİRİNTİ
# --------------------------------------------------------------------------
@login_required(login_url='login')
def qr_scanner_view(request):
    """Personelin uygulama içinden QR kod okutması için tarayıcı sayfasını gösterir."""
    # Bu view sadece template'i render eder, asıl iş JavaScript'te.
    context = {'user': request.user}
    return render(request, 'qr_scanner.html', context)