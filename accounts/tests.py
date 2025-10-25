# accounts/tests.py (En Güncel ve Tam Hali - ProfileView Test Düzeltmeleri Dahil - 25 Ekim 2025)

from django.test import TestCase, Client # Client eklendi
from django.urls import reverse # reverse eklendi
# Gerekli modelleri ve yardımcıları import et
from django.contrib.auth.models import User, Group # Group eklendi
from .models import Branch, Shift, Profile, Break, LeaveRequest # Profile ve Break eklendi
# Formları import et (testlerde type kontrolü için)
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserProfileUpdateForm, LeaveRequestForm
from datetime import date, time, datetime, timedelta # Tarih ve saat işlemleri için
from django.utils import timezone # Saat dilimi işlemleri için
from django.contrib.messages import get_messages # Yönlendirme sonrası mesajları test etmek için
from django.core import mail
from .forms import PersonnelAddForm, LeaveRequestForm, UserProfileUpdateForm

# --------------------------------------------------------------------------
# MODEL TESTLERİ
# --------------------------------------------------------------------------

class BranchModelTests(TestCase):
    """Branch modeli için testler."""

    def test_branch_creation_and_str(self):
        branch_name = "Merkez Şube Test"
        branch = Branch.objects.create(name=branch_name)
        self.assertEqual(str(branch), branch_name)
        self.assertEqual(Branch.objects.count(), 1)
        retrieved_branch = Branch.objects.get(id=branch.id)
        self.assertEqual(retrieved_branch.name, branch_name)

class ShiftModelTests(TestCase):
    """Shift modelinin (özellikle save metodu) testleri."""

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testpersonnel', password='password123')
        cls.test_branch = Branch.objects.create(name='Test Şube')
        cls.test_date = date(2025, 10, 23)
        cls.tz = timezone.get_current_timezone()

    # ... (Shift model test fonksiyonları öncekiyle aynı, buraya tekrar eklemiyorum) ...
    def test_shift_save_sabahci(self):
        shift = Shift.objects.create(personnel=self.test_user, branch=self.test_branch, date=self.test_date, shift_type='SABAH')
        expected_start = timezone.make_aware(datetime.combine(self.test_date, time(7, 30)), self.tz)
        expected_end = timezone.make_aware(datetime.combine(self.test_date, time(16, 30)), self.tz)
        self.assertEqual(shift.start_time, expected_start); self.assertEqual(shift.end_time, expected_end)
    def test_shift_save_araci(self):
        shift = Shift.objects.create(personnel=self.test_user, branch=self.test_branch, date=self.test_date, shift_type='ARACI')
        expected_start = timezone.make_aware(datetime.combine(self.test_date, time(11, 30)), self.tz)
        expected_end = timezone.make_aware(datetime.combine(self.test_date, time(20, 30)), self.tz)
        self.assertEqual(shift.start_time, expected_start); self.assertEqual(shift.end_time, expected_end)
    def test_shift_save_aksamci(self):
        shift = Shift.objects.create(personnel=self.test_user, branch=self.test_branch, date=self.test_date, shift_type='AKSAM')
        expected_start = timezone.make_aware(datetime.combine(self.test_date, time(15, 30)), self.tz)
        next_day = self.test_date + timedelta(days=1)
        expected_end = timezone.make_aware(datetime.combine(next_day, time(0, 30)), self.tz)
        self.assertEqual(shift.start_time, expected_start); self.assertEqual(shift.end_time, expected_end)
        self.assertEqual(shift.end_time.date(), shift.start_time.date() + timedelta(days=1))
    def test_shift_save_izinli(self):
        shift = Shift.objects.create(personnel=self.test_user, branch=self.test_branch, date=self.test_date, shift_type='IZIN')
        self.assertIsNone(shift.start_time); self.assertIsNone(shift.end_time)
    def test_shift_save_raporlu(self):
        shift = Shift.objects.create(personnel=self.test_user, branch=self.test_branch, date=self.test_date, shift_type='RAPORLU')
        self.assertIsNone(shift.start_time); self.assertIsNone(shift.end_time)
    def test_shift_save_devamsiz(self):
        shift = Shift.objects.create(personnel=self.test_user, branch=self.test_branch, date=self.test_date, shift_type='DEVAMSIZ')
        self.assertIsNone(shift.start_time); self.assertIsNone(shift.end_time)
    def test_shift_save_etkinlik_normal(self):
        custom_start, custom_end = time(10, 0), time(14, 30)
        shift = Shift.objects.create(personnel=self.test_user, branch=self.test_branch, date=self.test_date, shift_type='ETKINLIK', custom_start_time=custom_start, custom_end_time=custom_end)
        expected_start = timezone.make_aware(datetime.combine(self.test_date, custom_start), self.tz)
        expected_end = timezone.make_aware(datetime.combine(self.test_date, custom_end), self.tz)
        self.assertEqual(shift.start_time, expected_start); self.assertEqual(shift.end_time, expected_end)
    def test_shift_save_etkinlik_gece_yarisi(self):
        custom_start, custom_end = time(22, 0), time(2, 0)
        shift = Shift.objects.create(personnel=self.test_user, branch=self.test_branch, date=self.test_date, shift_type='ETKINLIK', custom_start_time=custom_start, custom_end_time=custom_end)
        expected_start = timezone.make_aware(datetime.combine(self.test_date, custom_start), self.tz)
        next_day = self.test_date + timedelta(days=1)
        expected_end = timezone.make_aware(datetime.combine(next_day, custom_end), self.tz)
        self.assertEqual(shift.start_time, expected_start); self.assertEqual(shift.end_time, expected_end)
        self.assertEqual(shift.end_time.date(), shift.start_time.date() + timedelta(days=1))
    def test_shift_save_etkinlik_saat_yoksa_none(self):
        shift = Shift.objects.create(personnel=self.test_user, branch=self.test_branch, date=self.test_date, shift_type='ETKINLIK')
        self.assertIsNone(shift.start_time); self.assertIsNone(shift.end_time)


# --------------------------------------------------------------------------
# VIEW TESTLERİ
# --------------------------------------------------------------------------

class LoginViewTests(TestCase):
    """login_view fonksiyonu için testler."""
    def setUp(self):
        self.client = Client(); self.login_url = reverse('login'); self.dashboard_url = reverse('accounts:dashboard')
        self.test_username = 'testloginuser'; self.test_password = 'testpassword123'
        self.user = User.objects.create_user(username=self.test_username, password=self.test_password)

    # ... (Login view test fonksiyonları öncekiyle aynı, buraya tekrar eklemiyorum) ...
    def test_login_page_loads_correctly(self):
        response = self.client.get(self.login_url); self.assertEqual(response.status_code, 200)
    def test_login_page_uses_correct_template(self):
        response = self.client.get(self.login_url); self.assertEqual(response.status_code, 200); self.assertTemplateUsed(response, 'index.html')
    def test_invalid_login_attempt(self):
        response = self.client.post(self.login_url, {'username': self.test_username, 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200); self.assertTemplateUsed(response, 'index.html'); self.assertContains(response, "Kullanıcı adı veya şifre hatalı."); self.assertFalse(response.wsgi_request.user.is_authenticated)
    def test_valid_login_attempt_redirects_to_dashboard(self):
        response = self.client.post(self.login_url, {'username': self.test_username, 'password': self.test_password}, follow=False)
        self.assertEqual(response.status_code, 302); self.assertRedirects(response, self.dashboard_url)
        response_followed = self.client.post(self.login_url, {'username': self.test_username, 'password': self.test_password}, follow=True)
        self.assertEqual(response_followed.status_code, 200); self.assertTemplateUsed(response_followed, 'dashboard.html'); self.assertTrue(response_followed.wsgi_request.user.is_authenticated); self.assertEqual(response_followed.wsgi_request.user.username, self.test_username)
    def test_logged_in_user_redirected_from_login_page(self):
        self.client.login(username=self.test_username, password=self.test_password); response = self.client.get(self.login_url, follow=False)
        self.assertEqual(response.status_code, 302); self.assertRedirects(response, self.dashboard_url)


class DashboardViewTests(TestCase):
    """dashboard_view fonksiyonu için testler (rol bazlı)."""
    @classmethod
    def setUpTestData(cls):
        cls.client = Client(); cls.dashboard_url = reverse('accounts:dashboard'); cls.login_url = reverse('login')
        cls.branch1 = Branch.objects.create(name='Test Şube 1')
        cls.user_password='password123'; cls.superuser_password='superpassword123'; cls.regional_password='regionalpass123'
        cls.user = User.objects.create_user(username='testpersonnel', password=cls.user_password, first_name='Test', last_name='Personel'); cls.user_profile = Profile.objects.create(user=cls.user, branch=cls.branch1)
        cls.superuser = User.objects.create_superuser(username='testadmin', password=cls.superuser_password, email='admin@test.com')
        cls.chef_group=Group.objects.create(name='Şube Şefi'); cls.manager_group=Group.objects.create(name='Bölge Yöneticisi')
        cls.user.groups.add(cls.chef_group)
        cls.regional_manager=User.objects.create_user(username='bolgemuduru', password=cls.regional_password); cls.regional_manager.groups.add(cls.manager_group); Profile.objects.create(user=cls.regional_manager, branch=cls.branch1)

    # ... (Dashboard view test fonksiyonları öncekiyle aynı, buraya tekrar eklemiyorum) ...
    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(self.dashboard_url); expected_redirect_url = f"{self.login_url}?next={self.dashboard_url}"; self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)
    def test_regular_personnel_view(self):
        normal_user=User.objects.create_user(username='normaluser', password='password123'); Profile.objects.create(user=normal_user, branch=self.branch1)
        self.client.login(username='normaluser', password='password123'); response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200); self.assertTemplateUsed(response, 'dashboard.html'); self.assertFalse(response.context['is_admin']); self.assertContains(response, "Kullanıcı Ekranı"); self.assertContains(response, "Yeni İzin/Rapor Talebi Oluştur"); self.assertContains(response, "<div id='calendar'>"); self.assertNotContains(response, "Yönetici Paneli"); self.assertNotContains(response, "Haftalık Vardiya Planla")
    def test_superuser_view(self):
        self.client.login(username=self.superuser.username, password=self.superuser_password); response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200); self.assertTemplateUsed(response, 'dashboard.html'); self.assertTrue(response.context['is_admin']); self.assertContains(response, "Yönetici Paneli"); self.assertContains(response, "Haftalık Vardiya Planla"); self.assertContains(response, "Personel Yönetimi"); self.assertContains(response, "Bekleyen İzin/Rapor Talepleri"); self.assertContains(response, "Mola Süresini Aşanlar"); self.assertContains(response, "Haftalık Mola Raporu"); self.assertContains(response, "Aylık Puantaj Raporu"); self.assertContains(response, '<table class="report-table">'); self.assertNotContains(response, "<div id='calendar'>")
    def test_branch_manager_view(self):
        self.client.login(username=self.user.username, password=self.user_password); response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200); self.assertTemplateUsed(response, 'dashboard.html'); self.assertTrue(response.context['is_admin']); self.assertContains(response, "Yönetici Paneli"); self.assertContains(response, "Haftalık Vardiya Planla"); self.assertContains(response, "Personel Yönetimi"); self.assertContains(response, "Bekleyen İzin/Rapor Talepleri"); self.assertNotContains(response, "Mola Süresini Aşanlar"); self.assertNotContains(response, "Haftalık Mola Raporu"); self.assertNotContains(response, "Aylık Puantaj Raporu"); self.assertContains(response, '<table class="report-table">'); self.assertContains(response, f"{self.branch1.name} Şubesi Mola Takip Raporu"); self.assertNotContains(response, "<div id='calendar'>")
    def test_regional_manager_view(self):
        self.client.login(username=self.regional_manager.username, password=self.regional_password); response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200); self.assertTemplateUsed(response, 'dashboard.html'); self.assertTrue(response.context['is_admin']); self.assertContains(response, "Yönetici Paneli"); self.assertContains(response, "Haftalık Vardiya Planla"); self.assertContains(response, "Personel Yönetimi"); self.assertContains(response, "Bekleyen İzin/Rapor Talepleri"); self.assertContains(response, "Mola Süresini Aşanlar"); self.assertContains(response, "Haftalık Mola Raporu"); self.assertContains(response, "Aylık Puantaj Raporu"); self.assertContains(response, '<table class="report-table">'); self.assertContains(response, "Genel Mola Takip Raporu (Tüm Şubeler)"); self.assertNotContains(response, "<div id='calendar'>")


class ProfileViewTests(TestCase):
    """profile_view fonksiyonu için testler (bilgi/şifre güncelleme)."""
    def setUp(self):
        self.client = Client()
        self.profile_url = reverse('accounts:profile')
        self.login_url = reverse('login')
        self.user_password = 'testpassword123'
        self.user = User.objects.create_user(username='testprofileuser', password=self.user_password, first_name='Test', last_name='Kullanici', email='test@example.com')
        self.profile = Profile.objects.create(user=self.user, branch=None)

    def test_profile_page_redirects_anonymous(self):
        response = self.client.get(self.profile_url)
        expected_redirect_url = f"{self.login_url}?next={self.profile_url}"; self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

    def test_profile_page_loads_for_logged_in_user(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200); self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response, self.user.username); self.assertContains(response, self.user.first_name); self.assertContains(response, self.user.last_name); self.assertContains(response, self.user.email)
        self.assertIsInstance(response.context['user_form'], UserProfileUpdateForm); self.assertIsInstance(response.context['password_form'], PasswordChangeForm)

    def test_profile_update_success(self):
        self.client.login(username=self.user.username, password=self.user_password)
        new_first_name="Güncel"; new_last_name="KullaniciTest"; new_email="guncel@test.com"
        # POST isteğini yap (yönlendirmeyi takip etme)
        response = self.client.post(self.profile_url, {'first_name': new_first_name, 'last_name': new_last_name, 'email': new_email, 'update_profile': 'Bilgilerimi Güncelle'}, follow=False)
        self.assertEqual(response.status_code, 302); self.assertRedirects(response, self.profile_url)
        # Veritabanını kontrol et
        self.user.refresh_from_db(); self.assertEqual(self.user.first_name, new_first_name); self.assertEqual(self.user.last_name, new_last_name); self.assertEqual(self.user.email, new_email)
        # DÜZELTİLMİŞ MESAJ KONTROLÜ: Yönlendirme yanıtından mesajları al
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Profil bilgileriniz başarıyla güncellendi!")

    def test_profile_update_invalid_email(self):
        other_user = User.objects.create_user(username='otheruser', password='password', email='other@example.com')
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.post(self.profile_url, {'first_name': self.user.first_name, 'last_name': self.user.last_name, 'email': other_user.email, 'update_profile': 'Bilgilerimi Güncelle'})
        self.assertEqual(response.status_code, 200)
        # DÜZELTİLMİŞ HATA KONTROLÜ: assertContains ile
        self.assertContains(response, "Bu e-posta adresi zaten başka bir kullanıcı tarafından kullanılıyor.")

    def test_password_change_success(self):
        self.client.login(username=self.user.username, password=self.user_password)
        new_password = 'newpassword456'
        # POST isteğini yap (yönlendirmeyi takip etme)
        response = self.client.post(self.profile_url, {'old_password': self.user_password, 'new_password1': new_password, 'new_password2': new_password, 'change_password': 'Şifremi Güncelle'}, follow=False)
        self.assertEqual(response.status_code, 302); self.assertRedirects(response, self.profile_url)
        # Veritabanını ve girişi kontrol et
        self.user.refresh_from_db(); self.assertTrue(self.user.check_password(new_password))
        can_login_with_old = self.client.login(username=self.user.username, password=self.user_password); self.assertFalse(can_login_with_old)
        # DÜZELTİLMİŞ MESAJ KONTROLÜ: Yönlendirme yanıtından mesajları al
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Şifreniz başarıyla güncellendi!")

    def test_password_change_wrong_old_password(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.post(self.profile_url, {'old_password': 'wrongoldpassword', 'new_password1': 'newpassword456', 'new_password2': 'newpassword456', 'change_password': 'Şifremi Güncelle'})
        self.assertEqual(response.status_code, 200)
        # DÜZELTİLMİŞ HATA KONTROLÜ: assertContains ile (Doğru metinle)
        self.assertContains(response, "Eski parolanız yanlış girildi. Lütfen tekrar girin.")

    def test_password_change_mismatch_new_password(self):
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.post(self.profile_url, {'old_password': self.user_password, 'new_password1': 'newpassword456', 'new_password2': 'MISMATCHpassword789', 'change_password': 'Şifremi Güncelle'})
        self.assertEqual(response.status_code, 200)
        # DÜZELTİLMİŞ HATA KONTROLÜ: assertContains ile (Doğru metinle)
        self.assertContains(response, "İki parola alanı eşleşmedi.")

class LeaveRequestCreateViewTests(TestCase):
    """leave_request_create_view fonksiyonu için testler (Personel Talep Oluşturma)."""

    def setUp(self):
        """Her test için gerekli kullanıcı ve URL'leri oluştur."""
        self.client = Client()
        self.create_request_url = reverse('accounts:leave_request_create') # Talep oluşturma URL'i
        self.dashboard_url = reverse('accounts:dashboard')
        self.login_url = reverse('login')

        # Test kullanıcısı oluştur
        self.user_password = 'password123'
        self.user = User.objects.create_user(username='testpersonnel', password=self.user_password)
        # Profil (ve şube) de oluşturalım, ileride gerekebilir
        self.branch = Branch.objects.create(name='Test Şube')
        Profile.objects.create(user=self.user, branch=self.branch)

        # Geçerli form verileri için tarihleri ayarla
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.day_after_tomorrow = self.today + timedelta(days=2)
        self.past_date = self.today - timedelta(days=5) # Geçersiz tarih testi için

    # --- Test Fonksiyonları ---

    def test_anonymous_user_redirected_to_login(self):
        """Giriş yapmamış kullanıcının talep oluşturma sayfasına erişememesini test eder."""
        response = self.client.get(self.create_request_url)
        expected_redirect_url = f"{self.login_url}?next={self.create_request_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

    def test_get_request_loads_form_correctly_for_logged_in_user(self):
        """Giriş yapmış kullanıcının talep formunu (200 OK) görebildiğini test eder."""
        self.client.login(username=self.user.username, password=self.user_password)
        response = self.client.get(self.create_request_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leave_request_form.html')
        # Formun context'te ve doğru tipte olduğunu kontrol et
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], LeaveRequestForm)
        self.assertNotContains(response, "Talep oluşturulamadı.") # Hata mesajı olmamalı

    def test_valid_post_request_creates_request_and_redirects(self):
        """Geçerli bir form gönderiminin (POST) yeni bir LeaveRequest oluşturduğunu
           ve dashboard'a yönlendirdiğini test eder."""
        self.client.login(username=self.user.username, password=self.user_password)

        # Başlangıçta hiç talep olmamalı
        self.assertEqual(LeaveRequest.objects.count(), 0)

        valid_data = {
            'request_type': 'IZIN',
            'start_date': self.tomorrow.strftime('%Y-%m-%d'), # YYYY-MM-DD formatında gönder
            'end_date': self.day_after_tomorrow.strftime('%Y-%m-%d'),
            'reason': 'Test talebi açıklaması'
        }

        response = self.client.post(self.create_request_url, valid_data, follow=False) # Yönlendirmeyi takip etme

        # 1. Yönlendirmeyi kontrol et
        self.assertEqual(response.status_code, 302) # Yönlendirme (302 Found)
        self.assertRedirects(response, self.dashboard_url)

        # 2. Veritabanını kontrol et: 1 yeni kayıt oluşmuş mu?
        self.assertEqual(LeaveRequest.objects.count(), 1)
        new_request = LeaveRequest.objects.first()
        self.assertEqual(new_request.personnel, self.user)
        self.assertEqual(new_request.request_type, 'IZIN')
        self.assertEqual(new_request.start_date, self.tomorrow)
        self.assertEqual(new_request.end_date, self.day_after_tomorrow)
        self.assertEqual(new_request.reason, 'Test talebi açıklaması')
        self.assertEqual(new_request.status, 'BEKLIYOR') # Durum 'BEKLIYOR' olmalı

        # 3. Başarı mesajını kontrol et
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Talebiniz başarıyla oluşturuldu ve onaya gönderildi.')

    def test_invalid_post_request_past_date(self):
        """Geçmiş tarihli bir talep gönderildiğinde formun hata vermesini test eder."""
        self.client.login(username=self.user.username, password=self.user_password)

        invalid_data = {
            'request_type': 'RAPOR',
            'start_date': self.past_date.strftime('%Y-%m-%d'), # Geçmiş tarih
            'end_date': self.today.strftime('%Y-%m-%d'),
            'reason': ''
        }

        response = self.client.post(self.create_request_url, invalid_data) # Yönlendirme beklemiyoruz (200 OK)

        self.assertEqual(response.status_code, 200) # Aynı sayfada kalmalı
        self.assertTemplateUsed(response, 'leave_request_form.html')
        # forms.py'da tanımladığımız özel hata mesajını kontrol et
        self.assertContains(response, "Başlangıç tarihi bugünden veya gelecek bir tarihten önce olamaz.")
        # Veritabanına kayıt girilmemiş olmalı
        self.assertEqual(LeaveRequest.objects.count(), 0)

    def test_invalid_post_request_end_date_before_start_date(self):
        """Bitiş tarihi başlangıçtan önce olan bir talep gönderildiğinde
           formun hata vermesini test eder."""
        self.client.login(username=self.user.username, password=self.user_password)

        invalid_data = {
            'request_type': 'IZIN',
            'start_date': self.day_after_tomorrow.strftime('%Y-%m-%d'), # 2 gün sonrası
            'end_date': self.tomorrow.strftime('%Y-%m-%d'), # 1 gün sonrası (Hatalı)
            'reason': ''
        }

        response = self.client.post(self.create_request_url, invalid_data)

        self.assertEqual(response.status_code, 200) # Aynı sayfada kalmalı
        self.assertTemplateUsed(response, 'leave_request_form.html')
        # forms.py'da tanımladığımız özel hata mesajını kontrol et
        self.assertContains(response, "Bitiş tarihi başlangıç tarihinden önce olamaz.")
        # Veritabanına kayıt girilmemiş olmalı
        self.assertEqual(LeaveRequest.objects.count(), 0)


       # accounts/tests.py

# ... (Önceki Test Case Class'ları: BranchModelTests, ShiftModelTests, LoginViewTests, DashboardViewTests, LeaveRequestCreateViewTests) ...


# --- MY LEAVE REQUESTS VIEW TESTLERİ ---
class MyLeaveRequestsViewTests(TestCase):
    """my_leave_requests_view fonksiyonu için testler (Personel Kendi Taleplerini Listeleme)."""

    @classmethod
    def setUpTestData(cls):
        """Testler için gerekli kullanıcıları ve talepleri oluştur."""
        cls.client = Client()
        cls.my_requests_url = reverse('accounts:my_leave_requests') # '/app/leave/my-requests/'
        cls.login_url = reverse('login') # '/'
        cls.password = 'password123'

        # User 1 (Talepleri olan)
        cls.user1 = User.objects.create_user(username='user1', password=cls.password)
        cls.request_user1_izin = LeaveRequest.objects.create(
            personnel=cls.user1,
            request_type='IZIN',
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 2),
            reason="User 1 Izin"
        )
        # User 1 için başka bir talep (Onaylanmış)
        cls.request_user1_rapor = LeaveRequest.objects.create(
            personnel=cls.user1,
            request_type='RAPOR',
            start_date=date(2025, 11, 5),
            end_date=date(2025, 11, 5),
            reason="User 1 Rapor",
            status='ONAYLANDI' # Durumu farklı olsun
        )

        # User 2 (Talebi olan başka bir kullanıcı)
        cls.user2 = User.objects.create_user(username='user2', password=cls.password)
        cls.request_user2_izin = LeaveRequest.objects.create(
            personnel=cls.user2,
            request_type='IZIN',
            start_date=date(2025, 11, 10),
            end_date=date(2025, 11, 10),
            reason="User 2 Izin (GÖRÜNMEMELİ)"
        )

        # User 3 (Hiç talebi olmayan)
        cls.user3 = User.objects.create_user(username='user3', password=cls.password)

    def test_anonymous_user_redirected_to_login(self):
        """Giriş yapmamış kullanıcının 'Taleplerim' sayfasına erişememesini test eder."""
        response = self.client.get(self.my_requests_url)
        expected_redirect_url = f"{self.login_url}?next={self.my_requests_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

    def test_user_sees_own_requests_and_template(self):
        """Giriş yapmış kullanıcının (User 1) kendi taleplerini gördüğünü
           ve doğru template'in kullanıldığını test eder."""
        self.client.login(username=self.user1.username, password=self.password)
        response = self.client.get(self.my_requests_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_leave_requests.html')

        # Context'teki listenin sadece user1'in taleplerini içerdiğini kontrol et
        self.assertIn('my_requests', response.context)
        # Talepler en yeniden eskiye sıralanmalı (created_at)
        self.assertEqual(len(response.context['my_requests']), 2) # Toplam 2 talebi var
        self.assertIn(self.request_user1_izin, response.context['my_requests'])
        self.assertIn(self.request_user1_rapor, response.context['my_requests'])

        # HTML içeriğinde kendi taleplerinin göründüğünü kontrol et
        self.assertContains(response, "User 1 Izin") # Kendi iznini görmeli
        self.assertContains(response, "User 1 Rapor") # Kendi raporunu görmeli
        self.assertContains(response, "Onaylandı") # Onaylanan talebin durumunu görmeli
        self.assertNotContains(response, "Daha önce oluşturulmuş bir talebiniz bulunmamaktadır.")

    def test_user_does_not_see_other_users_requests(self):
        """Giriş yapmış kullanıcının (User 1) başka bir kullanıcının (User 2)
           taleplerini GÖRMEDİĞİNİ test eder (Veri İzolasyonu)."""
        self.client.login(username=self.user1.username, password=self.password)
        response = self.client.get(self.my_requests_url)

        self.assertEqual(response.status_code, 200)
        # Kendi talebi görünmeli
        self.assertContains(response, "User 1 Izin")
        # Başkasının talebi görünmemeli
        self.assertNotContains(response, "User 2 Izin (GÖRÜNMEMELİ)")

    def test_user_with_no_requests_sees_message(self):
        """Hiç talebi olmayan bir kullanıcının (User 3) 'talep yok'
           mesajını gördüğünü test eder."""
        self.client.login(username=self.user3.username, password=self.password)
        response = self.client.get(self.my_requests_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_leave_requests.html')
        # Context'teki listenin boş olduğunu kontrol et
        self.assertIn('my_requests', response.context)
        self.assertEqual(len(response.context['my_requests']), 0) # Talep listesi boş olmalı
        # HTML'de doğru mesajın göründüğünü kontrol et
        self.assertContains(response, "Daha önce oluşturulmuş bir talebiniz bulunmamaktadır.")

# --- Buraya gelecekte diğer view testleri eklenecek ---


# accounts/tests.py

# ... (Önceki Test Case Class'ları) ...


# --- PENDING LEAVE REQUESTS VIEW TESTLERİ ---
class PendingLeaveRequestsViewTests(TestCase):
    """pending_leave_requests_view fonksiyonu için testler (Yönetici Onay Listesi)."""

    @classmethod
    def setUpTestData(cls):
        """Testler için farklı şubeler, roller ve talepler oluştur."""
        cls.client = Client()
        cls.pending_url = reverse('accounts:pending_leave_requests') # '/app/leave/pending/'
        cls.login_url = reverse('login')
        cls.dashboard_url = reverse('accounts:dashboard')
        cls.password = 'password123'

        # Şubeler
        cls.branch_A = Branch.objects.create(name='Şube A')
        cls.branch_B = Branch.objects.create(name='Şube B')

        # Roller (Gruplar)
        cls.chef_group = Group.objects.create(name='Şube Şefi')
        cls.manager_group = Group.objects.create(name='Bölge Yöneticisi')

        # Kullanıcılar
        # Superuser
        cls.superuser = User.objects.create_superuser(username='superadmin', password=cls.password)

        # Şube Şefi A (Sadece Şube A'yı görebilmeli)
        cls.chef_A = User.objects.create_user(username='sef_A', password=cls.password)
        cls.chef_A.groups.add(cls.chef_group)
        Profile.objects.create(user=cls.chef_A, branch=cls.branch_A)

        # Bölge Yöneticisi (Her şeyi görebilmeli)
        cls.regional_manager = User.objects.create_user(username='bolgeyoneticisi', password=cls.password)
        cls.regional_manager.groups.add(cls.manager_group)
        Profile.objects.create(user=cls.regional_manager, branch=cls.branch_A) # Hangi şubede olduğu fark etmez

        # Personel 1 (Şube A)
        cls.personnel_A1 = User.objects.create_user(username='personel_A1', password=cls.password)
        Profile.objects.create(user=cls.personnel_A1, branch=cls.branch_A)

        # Personel 2 (Şube B)
        cls.personnel_B1 = User.objects.create_user(username='personel_B1', password=cls.password)
        Profile.objects.create(user=cls.personnel_B1, branch=cls.branch_B)

        # Personel 3 (Normal, yetkisiz)
        cls.normal_user = User.objects.create_user(username='normaluser', password=cls.password)
        Profile.objects.create(user=cls.normal_user, branch=cls.branch_A)

        # Talepler
        cls.today = timezone.now().date()
        # 1. Şube A'dan Bekleyen Talep
        cls.req_A_pending = LeaveRequest.objects.create(
            personnel=cls.personnel_A1, request_type='IZIN', status='BEKLIYOR',
            start_date=cls.today + timedelta(days=5), end_date=cls.today + timedelta(days=6), reason="Şube A Bekliyor")
        # 2. Şube B'den Bekleyen Talep
        cls.req_B_pending = LeaveRequest.objects.create(
            personnel=cls.personnel_B1, request_type='RAPOR', status='BEKLIYOR',
            start_date=cls.today + timedelta(days=7), end_date=cls.today + timedelta(days=7), reason="Şube B Bekliyor")
        # 3. Şube A'dan Onaylanmış Talep (Listede görünmemeli)
        cls.req_A_approved = LeaveRequest.objects.create(
            personnel=cls.personnel_A1, request_type='IZIN', status='ONAYLANDI',
            start_date=cls.today + timedelta(days=1), end_date=cls.today + timedelta(days=1), reason="Şube A Onaylandı")

    def test_anonymous_user_redirected_to_login(self):
        """Giriş yapmamış kullanıcının bekleyen talepler sayfasına erişememesini test eder."""
        response = self.client.get(self.pending_url)
        expected_redirect_url = f"{self.login_url}?next={self.pending_url}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

   # accounts/tests.py -> PendingLeaveRequestsViewTests içi

    def test_normal_personnel_redirected_to_dashboard(self):
        """Normal personelin (yetkisiz) bekleyen talepler sayfasına erişememesini test eder."""
        self.client.login(username=self.normal_user.username, password=self.password)

        # DÜZELTME: response = self.client.get(self.pending_url) YERİNE,
        # follow=True ekleyerek Django'nun yönlendirmeyi takip etmesini
        # ve bize *son ulaşılan sayfayı* vermesini istiyoruz.
        response = self.client.get(self.pending_url, follow=True) 

        # Artık assertRedirects'e gerek yok.
        # Sadece son ulaşılan sayfanın durumunu ve içeriğini kontrol edeceğiz.

        # Yönlendirme sonrası ulaşılan sayfa (dashboard) başarılı yüklendi mi (200 OK)?
        self.assertEqual(response.status_code, 200)

        # Ulaşılan sayfa gerçekten 'dashboard.html' mi?
        self.assertTemplateUsed(response, 'dashboard.html')

        # Ulaşılan sayfa gerçekten personel dashboard'u mu (admin değil mi)?
        self.assertFalse(response.context['is_admin'])
        self.assertContains(response, "Kullanıcı Ekranı")

    def test_branch_manager_sees_only_own_branch_requests(self):
        """Şube Şefi'nin SADECE kendi şubesinin bekleyen taleplerini gördüğünü test eder."""
        self.client.login(username=self.chef_A.username, password=self.password) # Şube A Şefi
        response = self.client.get(self.pending_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pending_leave_requests.html')
        # Context'teki listeyi kontrol et
        self.assertIn('pending_requests', response.context)
        self.assertEqual(len(response.context['pending_requests']), 1) # Sadece 1 talep görmeli
        self.assertIn(self.req_A_pending, response.context['pending_requests']) # Şube A'nın talebi
        self.assertNotIn(self.req_B_pending, response.context['pending_requests']) # Şube B'nin talebi YOK
        # HTML içeriğini kontrol et
        self.assertContains(response, "Şube A Bekliyor")
        self.assertNotContains(response, "Şube B Bekliyor")
        self.assertNotContains(response, "Şube A Onaylandı") # Onaylanmış olan görünmemeli

    def test_regional_manager_sees_all_pending_requests(self):
        """Bölge Yöneticisi'nin TÜM şubelerin bekleyen taleplerini gördüğünü test eder."""
        self.client.login(username=self.regional_manager.username, password=self.password)
        response = self.client.get(self.pending_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pending_leave_requests.html')
        # Context'teki listeyi kontrol et
        self.assertIn('pending_requests', response.context)
        self.assertEqual(len(response.context['pending_requests']), 2) # Toplam 2 bekleyen talep görmeli
        self.assertIn(self.req_A_pending, response.context['pending_requests']) # Şube A'nın talebi
        self.assertIn(self.req_B_pending, response.context['pending_requests']) # Şube B'nin talebi
        # HTML içeriğini kontrol et
        self.assertContains(response, "Şube A Bekliyor")
        self.assertContains(response, "Şube B Bekliyor")
        self.assertNotContains(response, "Şube A Onaylandı") # Onaylanmış olan görünmemeli

    def test_superuser_sees_all_pending_requests(self):
        """Superuser'ın TÜM şubelerin bekleyen taleplerini gördüğünü test eder."""
        self.client.login(username=self.superuser.username, password=self.password)
        response = self.client.get(self.pending_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pending_leave_requests.html')
        # Context'teki listeyi kontrol et
        self.assertIn('pending_requests', response.context)
        self.assertEqual(len(response.context['pending_requests']), 2) # Toplam 2 bekleyen talep görmeli
        self.assertIn(self.req_A_pending, response.context['pending_requests'])
        self.assertIn(self.req_B_pending, response.context['pending_requests'])
        # HTML içeriğini kontrol et
        self.assertContains(response, "Şube A Bekliyor")
        self.assertContains(response, "Şube B Bekliyor")
        self.assertNotContains(response, "Şube A Onaylandı")

    def test_no_pending_requests_shows_message(self):
        """Hiç bekleyen talep olmadığında 'talep yok' mesajının göründüğünü test eder."""
        # Mevcut bekleyen talepleri silelim (sadece bu test için)
        LeaveRequest.objects.filter(status='BEKLIYOR').delete()

        self.client.login(username=self.superuser.username, password=self.password)
        response = self.client.get(self.pending_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('pending_requests', response.context)
        self.assertEqual(len(response.context['pending_requests']), 0) # Liste boş olmalı
        self.assertContains(response, "Onay bekleyen talep bulunmamaktadır.")

# --- Buraya gelecekte diğer view testleri eklenecek ---


# accounts/tests.py

# ... (Önceki Test Case Class'ları) ...


# --- PROCESS LEAVE REQUEST VIEW TESTLERİ ---
class ProcessLeaveRequestViewTests(TestCase):
    """process_leave_request_view fonksiyonu için testler (Onay/Red)."""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.password = 'password123'
        cls.pending_list_url = reverse('accounts:pending_leave_requests')
        cls.dashboard_url = reverse('accounts:dashboard')

        # Şubeler ve Roller
        cls.branch_A = Branch.objects.create(name='Şube A')
        cls.branch_B = Branch.objects.create(name='Şube B')
        cls.chef_group = Group.objects.create(name='Şube Şefi')
        cls.manager_group = Group.objects.create(name='Bölge Yöneticisi')

        # Kullanıcılar
        cls.chef_A = User.objects.create_user(username='sef_A', password=cls.password)
        cls.chef_A.groups.add(cls.chef_group)
        Profile.objects.create(user=cls.chef_A, branch=cls.branch_A)

        cls.regional_manager = User.objects.create_user(username='bolgeyoneticisi', password=cls.password)
        cls.regional_manager.groups.add(cls.manager_group)
        Profile.objects.create(user=cls.regional_manager, branch=cls.branch_A)

        cls.personnel_A = User.objects.create_user(username='personel_A', password=cls.password, email='personelA@test.com')
        Profile.objects.create(user=cls.personnel_A, branch=cls.branch_A)

        cls.personnel_B = User.objects.create_user(username='personel_B', password=cls.password, email='personelB@test.com')
        Profile.objects.create(user=cls.personnel_B, branch=cls.branch_B)

        cls.normal_user = User.objects.create_user(username='normaluser', password=cls.password)
        Profile.objects.create(user=cls.normal_user, branch=cls.branch_A)

    def setUp(self):
        """Her testten önce çalışır, taze talep oluşturur (diğer testlerde değiştirilmemiş olur)"""
        self.client.logout() # Her teste temiz başla

        # Testler için taze talepler
        self.today = timezone.now().date()
        self.req_A = LeaveRequest.objects.create(
            personnel=self.personnel_A, request_type='IZIN', status='BEKLIYOR',
            start_date=self.today + timedelta(days=5), end_date=self.today + timedelta(days=6), reason="Onay Testi")

        self.req_B = LeaveRequest.objects.create(
            personnel=self.personnel_B, request_type='RAPOR', status='BEKLIYOR',
            start_date=self.today + timedelta(days=7), end_date=self.today + timedelta(days=7), reason="Red Testi")

        # Talepleri işlemek için URL'ler
        self.process_url_A = reverse('accounts:process_leave_request', args=[self.req_A.id])
        self.process_url_B = reverse('accounts:process_leave_request', args=[self.req_B.id])

    def test_anonymous_user_cannot_process_request(self):
        """Giriş yapmamış kullanıcının talebi işleyememesini test eder."""
        response = self.client.post(self.process_url_A, {'action': 'approve'})
        self.assertNotEqual(response.status_code, 200) # Başarılı olmamalı
        self.req_A.refresh_from_db()
        self.assertEqual(self.req_A.status, 'BEKLIYOR') # Durum değişmemeli

    def test_normal_personnel_cannot_process_request(self):
        """Normal personelin talebi işleyememesini test eder."""
        self.client.login(username=self.normal_user.username, password=self.password)

        # DÜZELTME: response = self.client.post(...) YERİNE,
        # follow=True ekleyerek Django'nun yönlendirmeyi takip etmesini
        # ve bize *son ulaşılan sayfayı* vermesini istiyoruz.
        response = self.client.post(self.process_url_A, {'action': 'approve'}, follow=True) 

        # Artık assertRedirects'e gerek yok.
        # Sadece son ulaşılan sayfanın durumunu ve içeriğini kontrol edeceğiz.

        # Yönlendirme sonrası ulaşılan sayfa (dashboard) başarılı yüklendi mi (200 OK)?
        self.assertEqual(response.status_code, 200)

        # Ulaşılan sayfa gerçekten 'dashboard.html' mi?
        self.assertTemplateUsed(response, 'dashboard.html')

        # Ulaşılan sayfa gerçekten personel dashboard'u mu (admin değil mi)?
        self.assertFalse(response.context['is_admin'])
        self.assertContains(response, "Kullanıcı Ekranı")

        # Talebin durumunun değişmediğini de tekrar kontrol edelim
        self.req_A.refresh_from_db()
        self.assertEqual(self.req_A.status, 'BEKLIYOR')

    def test_branch_manager_cannot_process_other_branch_request(self):
        """Şube Şefi'nin (A) başka bir şubenin (B) talebini işleyememesini test eder."""
        self.client.login(username=self.chef_A.username, password=self.password) # Şube A Şefi
        response = self.client.post(self.process_url_B, {'action': 'approve'}, follow=True) # Şube B talebi

        self.assertRedirects(response, self.pending_list_url) # Listeye geri yönlendirilmeli
        self.assertContains(response, "Bu talebi işleme yetkiniz yok") # Hata mesajı
        self.req_B.refresh_from_db()
        self.assertEqual(self.req_B.status, 'BEKLIYOR') # Durum değişmemeli

    def test_get_request_is_redirected(self):
        """Talep işleme URL'ine GET isteği yapmanın listeye yönlendirdiğini test eder."""
        self.client.login(username=self.chef_A.username, password=self.password)
        response = self.client.get(self.process_url_A)
        self.assertRedirects(response, self.pending_list_url)

    def test_request_approve_success_by_branch_manager(self):
        """Şube Şefi'nin kendi şubesindeki talebi başarıyla ONAYLADIĞINI test eder."""
        self.client.login(username=self.chef_A.username, password=self.password) # Şube A Şefi

        # Başlangıçta Shift kaydı yok
        self.assertEqual(Shift.objects.filter(personnel=self.personnel_A, date=self.req_A.start_date).count(), 0)

        post_data = {
            'action': 'approve',
            'manager_notes': 'Hayırlı olsun.'
        }
        response = self.client.post(self.process_url_A, post_data, follow=True) # Şube A talebi

        # 1. Yönlendirmeyi ve mesajı kontrol et
        self.assertRedirects(response, self.pending_list_url) # Listeye yönlendirildi
        self.assertContains(response, "onaylandı ve vardiya planına işlendi") # Başarı mesajı

        # 2. LeaveRequest objesini kontrol et
        self.req_A.refresh_from_db()
        self.assertEqual(self.req_A.status, 'ONAYLANDI')
        self.assertEqual(self.req_A.processed_by, self.chef_A) # İşleyen kişi doğru mu?
        self.assertEqual(self.req_A.manager_notes, 'Hayırlı olsun.')
        self.assertIsNotNone(self.req_A.processed_at)

        # 3. Shift tablosunun güncellendiğini kontrol et
        self.assertEqual(Shift.objects.count(), 2) # 2 günlük izin
        shift1 = Shift.objects.get(personnel=self.personnel_A, date=self.req_A.start_date)
        shift2 = Shift.objects.get(personnel=self.personnel_A, date=self.req_A.end_date)
        self.assertEqual(shift1.shift_type, 'IZIN') # Doğru tip ('IZIN')
        self.assertEqual(shift2.shift_type, 'IZIN')
        self.assertEqual(shift1.branch, self.branch_A) # Personelin ana şubesi (A) atandı
        self.assertIsNone(shift1.start_time) # Saatler None olmalı

        # 4. E-posta gönderildi mi? (Konsola 1 e-posta basılmış olmalı)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"İzin/Rapor Talebiniz Onaylandı ({self.req_A.start_date.strftime('%d.%m')} - {self.req_A.end_date.strftime('%d.%m')})")
        self.assertIn("Hayırlı olsun.", mail.outbox[0].body)
        self.assertIn(self.personnel_A.email, mail.outbox[0].to)

    def test_request_reject_success_by_regional_manager(self):
        """Bölge Yöneticisi'nin bir talebi başarıyla REDDETTİĞİNİ test eder."""
        self.client.login(username=self.regional_manager.username, password=self.password) # Bölge Yöneticisi

        # Başlangıçta Shift kaydı yok
        self.assertEqual(Shift.objects.count(), 0)

        post_data = {
            'action': 'reject',
            'manager_notes': 'Personel eksikliği var.'
        }
        response = self.client.post(self.process_url_B, post_data, follow=True) # Şube B talebi

        # 1. Yönlendirmeyi ve mesajı kontrol et
        self.assertRedirects(response, self.pending_list_url) # Listeye yönlendirildi
        self.assertContains(response, "talebi reddedildi") # Başarı mesajı

        # 2. LeaveRequest objesini kontrol et
        self.req_B.refresh_from_db()
        self.assertEqual(self.req_B.status, 'REDDEDILDI')
        self.assertEqual(self.req_B.processed_by, self.regional_manager) # İşleyen kişi doğru mu?
        self.assertEqual(self.req_B.manager_notes, 'Personel eksikliği var.')
        self.assertIsNotNone(self.req_B.processed_at)

        # 3. Shift tablosunun güncellenmediğini (boş kaldığını) kontrol et
        self.assertEqual(Shift.objects.count(), 0) # Kayıt oluşturulmamalı

        # 4. E-posta gönderildi mi? (Konsola 1 e-posta basılmış olmalı)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"İzin/Rapor Talebiniz Reddedildi ({self.req_B.start_date.strftime('%d.%m')} - {self.req_B.end_date.strftime('%d.%m')})")
        self.assertIn("Personel eksikliği var.", mail.outbox[0].body)
        self.assertIn(self.personnel_B.email, mail.outbox[0].to)

# --- Buraya gelecekte diğer view testleri eklenecek ---

# accounts/tests.py

# ... (Önceki Test Case Class'ları) ...


# --- PERSONEL YÖNETİMİ VIEW TESTLERİ ---
class PersonnelManagementViewsTests(TestCase):
    """Personnel list, add, activate, deactivate view fonksiyonları için testler."""

    @classmethod
    def setUpTestData(cls):
        """Testler için gerekli kullanıcıları, grupları ve şubeyi oluştur."""
        cls.client = Client()
        cls.password = 'password123'

        # URL'ler
        cls.list_url = reverse('accounts:personnel_list')
        cls.add_url = reverse('accounts:personnel_add')
        cls.login_url = reverse('login')
        cls.dashboard_url = reverse('accounts:dashboard')

        # Şube ve Gruplar
        cls.branch = Branch.objects.create(name='Ana Şube')
        cls.chef_group = Group.objects.create(name='Şube Şefi')

        # Kullanıcılar
        cls.manager = User.objects.create_user(username='yonetici', password=cls.password)
        cls.manager.groups.add(cls.chef_group)
        Profile.objects.create(user=cls.manager, branch=cls.branch)

        cls.normal_user = User.objects.create_user(username='personel1', password=cls.password, first_name='Ali', last_name='Veli')
        Profile.objects.create(user=cls.normal_user, branch=cls.branch)

        cls.inactive_user = User.objects.create_user(username='eskiper', password=cls.password, is_active=False) # Dondurulmuş kullanıcı
        Profile.objects.create(user=cls.inactive_user, branch=cls.branch)

    # --- Yetki Testleri (Genel) ---

    def test_anonymous_redirected(self):
        """Giriş yapmamış kullanıcının personel yönetimi sayfalarına erişememesini test eder."""
        response_list = self.client.get(self.list_url)
        response_add = self.client.get(self.add_url)
        self.assertRedirects(response_list, f"{self.login_url}?next={self.list_url}")
        self.assertRedirects(response_add, f"{self.login_url}?next={self.add_url}")

    def test_normal_personnel_redirected(self):
        """Normal personelin personel yönetimi sayfalarına erişememesini test eder."""
        self.client.login(username=self.normal_user.username, password=self.password)
        response_list = self.client.get(self.list_url, follow=True) # Yönlendirmeyi takip et
        response_add = self.client.get(self.add_url, follow=True)

        # Her ikisi de dashboard'a yönlendirmeli ve dashboard'u göstermeli
        self.assertEqual(response_list.status_code, 200)
        self.assertTemplateUsed(response_list, 'dashboard.html')
        self.assertFalse(response_list.context['is_admin'])

        self.assertEqual(response_add.status_code, 200)
        self.assertTemplateUsed(response_add, 'dashboard.html')
        self.assertFalse(response_add.context['is_admin'])

    # --- personnel_list_view Testleri ---

    def test_manager_can_access_list_view(self):
        """Yöneticinin (Şef) personel listesini görebildiğini test eder."""
        self.client.login(username=self.manager.username, password=self.password)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personnel_list.html')
        # Listede hem aktif hem dondurulmuş kullanıcıların olmasını kontrol et
        self.assertContains(response, self.normal_user.username)
        self.assertContains(response, self.normal_user.profile.branch.name)
        self.assertContains(response, "Aktif")
        self.assertContains(response, self.inactive_user.username)
        self.assertContains(response, "Dondurulmuş")

    # --- personnel_add_view Testleri (GET ve POST) ---

    def test_manager_can_access_add_view_get(self):
        """Yöneticinin personel ekleme formunu (GET) görebildiğini test eder."""
        self.client.login(username=self.manager.username, password=self.password)
        response = self.client.get(self.add_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personnel_add.html')
        self.assertIsInstance(response.context['form'], PersonnelAddForm)

    def test_manager_can_add_personnel_success(self):
        """Yöneticinin başarıyla yeni personel ekleyebildiğini (POST) test eder."""
        self.client.login(username=self.manager.username, password=self.password)
        user_count_before = User.objects.count()
        profile_count_before = Profile.objects.count()

        new_personnel_data = {
            'username': 'yenipersonel',
            'first_name': 'Yeni',
            'last_name': 'Personel',
            'email': 'yeni@test.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'branch': self.branch.id # forms.py'daki şube alanı
        }
        response = self.client.post(self.add_url, new_personnel_data, follow=False) # Yönlendirmeyi takip etme

        # 1. Yönlendirmeyi kontrol et
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.list_url)

        # 2. Veritabanını kontrol et
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertEqual(Profile.objects.count(), profile_count_before + 1)
        new_user = User.objects.get(username='yenipersonel')
        self.assertEqual(new_user.first_name, 'Yeni')
        self.assertTrue(new_user.check_password('newpassword123')) # Şifre doğru hash'lendi mi?
        self.assertEqual(new_user.profile.branch, self.branch) # Profil ve şube doğru bağlandı mı?

        # 3. Başarı mesajını kontrol et
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("başarıyla eklendi", str(messages[0]))

    def test_add_personnel_password_mismatch(self):
        """Yeni personel eklerken şifreler eşleşmezse hata verdiğini test eder."""
        self.client.login(username=self.manager.username, password=self.password)
        user_count_before = User.objects.count()

        invalid_data = {
            'username': 'hataliper', 'first_name': 'Hata', 'last_name': 'Test',
            'password': 'password123',
            'confirm_password': 'PASSWORD_MISMATCH', # Hatalı tekrar
            'branch': self.branch.id
        }
        response = self.client.post(self.add_url, invalid_data)

        self.assertEqual(response.status_code, 200) # Aynı sayfada kalmalı
        self.assertTemplateUsed(response, 'personnel_add.html')
        self.assertContains(response, "Girilen şifreler eşleşmiyor.")
        self.assertEqual(User.objects.count(), user_count_before) # Yeni kullanıcı oluşmamalı

    # --- personnel_deactivate/activate_view Testleri (POST) ---

    def test_manager_can_deactivate_user(self):
        """Yöneticinin bir personeli dondurabildiğini (is_active=False) test eder."""
        self.client.login(username=self.manager.username, password=self.password)
        deactivate_url = reverse('accounts:personnel_deactivate', args=[self.normal_user.id])

        self.assertTrue(User.objects.get(id=self.normal_user.id).is_active) # Başlangıçta Aktif

        response = self.client.post(deactivate_url, follow=True) # Yönlendirmeyi takip et

        self.assertRedirects(response, self.list_url) # Listeye dönmeli
        self.assertContains(response, "hesabı donduruldu") # Mesajı kontrol et
        self.assertFalse(User.objects.get(id=self.normal_user.id).is_active) # Artık Aktif Değil

    def test_manager_can_activate_user(self):
        """Yöneticinin dondurulmuş bir personeli aktifleştirebildiğini (is_active=True) test eder."""
        self.client.login(username=self.manager.username, password=self.password)
        activate_url = reverse('accounts:personnel_activate', args=[self.inactive_user.id])

        self.assertFalse(User.objects.get(id=self.inactive_user.id).is_active) # Başlangıçta Aktif Değil

        response = self.client.post(activate_url, follow=True)

        self.assertRedirects(response, self.list_url) # Listeye dönmeli
        self.assertContains(response, "hesabı tekrar aktifleştirildi") # Mesajı kontrol et
        self.assertTrue(User.objects.get(id=self.inactive_user.id).is_active) # Artık Aktif