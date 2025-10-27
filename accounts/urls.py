# accounts/urls.py (En Güncel Hali - QR Tarayıcı Kaldırıldı - 27 Ekim 2025)

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
    # Bu URL artık manuel buton tarafından tetikleniyor
    path('mola/<int:branch_id>/toggle/',
         views.toggle_break_view,
         name='toggle_break'),
    # 'scan/' URL'i buradan kaldırıldı.

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

    # --- İzin/Rapor Talepleri (Personel + Yönetici) ---
    path('leave/request/',
         views.leave_request_create_view, # Talep Oluşturma
         name='leave_request_create'),
    path('leave/my-requests/',
         views.my_leave_requests_view, # Personelin Talepleri
         name='my_leave_requests'),
    path('leave/pending/',
         views.pending_leave_requests_view, # Yöneticinin Bekleyen Talepleri
         name='pending_leave_requests'),
    path('leave/process/<int:request_id>/',
         views.process_leave_request_view, # Yöneticinin Talep İşleme
         name='process_leave_request'),
]