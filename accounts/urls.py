# accounts/urls.py (En Güncel ve Tam Hali - 23 Ekim 2025)

from django.urls import path
# Bulunduğumuz 'accounts' klasöründeki views.py dosyasını import ediyoruz
from . import views

# Uygulama adı (namespace): Template'lerde {% url 'accounts:...' %} gibi
# kullanmamızı sağlar ve URL isimlerinin diğer uygulamalarla çakışmasını önler.
app_name = 'accounts'

urlpatterns = [
    # --- Temel Hesap İşlemleri ---
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'), # Profil sayfası

    # --- Mola İşlemleri ---
    path('mola/<int:branch_id>/toggle/',
         views.toggle_break_view,
         name='toggle_break'),

    # --- Raporlar (Yöneticiler İçin) ---
    path('reports/exceeded-breaks/',
         views.exceeded_breaks_report_view,
         name='exceeded_breaks_report'), # Mola Süresini Aşanlar
    path('reports/breaks/weekly/select/',
         views.break_report_select_view,
         name='break_report_select'), # Haftalık Mola Raporu - Şube Seçimi
    path('reports/breaks/weekly/<int:branch_id>/',
         views.break_report_weekly_view,
         name='break_report_weekly'), # Haftalık Mola Raporu - Şube Detayı
    path('reports/attendance/monthly/select/',
         views.attendance_report_select_view,
         name='attendance_report_select'), # Aylık Puantaj - Şube/Ay Seçimi
    path('reports/attendance/monthly/<int:branch_id>/<int:year>/<int:month>/',
         views.attendance_report_monthly_view,
         name='attendance_report_monthly'), # Aylık Puantaj - Rapor Detayı

    # --- Haftalık Vardiya Planlama (Yöneticiler İçin) ---
    path('schedule/weekly/',
         views.weekly_schedule_select_view,
         name='weekly_schedule_select'), # Şube Seçimi
    path('schedule/weekly/<int:branch_id>/',
         views.weekly_schedule_view,
         name='weekly_schedule_branch'), # Planlama Ekranı

    # --- Personel Yönetimi (Yöneticiler İçin) ---
    path('personnel/',
         views.personnel_list_view,
         name='personnel_list'), # Personel Listesi
    path('personnel/add/',
         views.personnel_add_view,
         name='personnel_add'), # Personel Ekleme
    path('personnel/<int:user_id>/deactivate/',
         views.personnel_deactivate_view,
         name='personnel_deactivate'), # Personel Dondurma
    path('personnel/<int:user_id>/activate/',
         views.personnel_activate_view,
         name='personnel_activate'), # Personel Aktifleştirme

    # --- İzin/Rapor Talepleri (Personel İçin) ---
    path('leave/request/',
         views.leave_request_create_view, # Talep Oluşturma
         name='leave_request_create'),
    # Gelecekte eklenecek taleplerle ilgili diğer URL'ler buraya gelecek
    # (Taleplerim, Bekleyen Talepler, Onayla, Reddet vb.)

    path('leave/my-requests/',
         views.my_leave_requests_view, # YENİ FONKSİYON
         name='my_leave_requests'),

    # --- Yönetici URL'leri (önceden eklenmişti) ---
    path('leave/pending/',
         views.pending_leave_requests_view,
         name='pending_leave_requests'),
    path('leave/process/<int:request_id>/',
         views.process_leave_request_view,
         name='process_leave_request'),

    path('leave/request/',
         views.leave_request_create_view, # Personel için Talep Oluşturma
         name='leave_request_create'),

    # YENİ EKLENEN YÖNETİCİ URL'leri:
    # 1. Bekleyen Talepler Listesi -> /app/leave/pending/
    path('leave/pending/',
         views.pending_leave_requests_view, # YENİ FONKSİYON
         name='pending_leave_requests'),

    # 2. Talebi İşleme (Onaylama/Reddetme) -> /app/leave/process/<request_id>/
    path('leave/process/<int:request_id>/',
         views.process_leave_request_view, # YENİ FONKSİYON
         name='process_leave_request'),

path('scan/',
         views.qr_scanner_view, # YENİ FONKSİYON
         name='qr_scanner'),
]