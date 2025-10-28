# accounts/forms.py (En Güncel ve Tam Hali)

from django import forms
from django.contrib.auth.forms import UserCreationForm # Personel eklerken şifre için kullanıldı
from django.contrib.auth.models import User
from django.utils import timezone # LeaveRequestForm'da tarih kontrolü için
from .models import Branch, LeaveRequest # Modelleri import ediyoruz

# --------------------------------------------------------------------------
# 1. YÖNETİCİ İÇİN YENİ PERSONEL EKLEME FORMU
# --------------------------------------------------------------------------
class PersonnelAddForm(forms.ModelForm):
    """Yöneticilerin yeni personel eklemesi için form."""
    # Şifre alanları
    password = forms.CharField(label="Şifre", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Şifre (Tekrar)", widget=forms.PasswordInput)
    # Şube seçimi
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all().order_by('name'), # Şubeleri isme göre sırala
        label="Atanacak Şube",
        required=False, # Şube seçimi zorunlu
        empty_label="--- Lütfen Şube Seçin ---" # Boş seçenek metni
    )

    class Meta:
        model = User
        # Formda görünecek User model alanları
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = { # Alan etiketlerini Türkçeleştir
            'username': 'Kullanıcı Adı (Giriş için)',
            'first_name': 'Adı',
            'last_name': 'Soyadı',
            'email': 'E-posta (İsteğe Bağlı)',
        }
        help_texts = { # Yardımcı metinler
            'username': 'Personelin sisteme giriş yaparken kullanacağı benzersiz ad.',
        }

    def clean_confirm_password(self):
        """Şifrelerin eşleşip eşleşmediğini kontrol eder."""
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Girilen şifreler eşleşmiyor.")
        # Django'nun kendi şifre doğrulama mekanizmalarını da ekleyebiliriz (opsiyonel)
        # try:
        #     from django.contrib.auth.password_validation import validate_password
        #     validate_password(password, self.instance) # self.instance User objesi
        # except forms.ValidationError as e:
        #     self.add_error('password', e)
        return confirm_password

    def save(self, commit=True):
        """Form kaydedildiğinde User oluşturur ve şifreyi ayarlar."""
        # User objesini oluştur ama veritabanına kaydetme
        user = super().save(commit=False)
        # Şifreyi hashleyerek ayarla
        user.set_password(self.cleaned_data["password"])
        # Yeni kullanıcıları varsayılan olarak 'aktif' yapalım
        user.is_active = True
        # Yeni kullanıcılar staff veya superuser olmamalı (varsayılan)
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save() # Şimdi User'ı kaydet
        return user

# --------------------------------------------------------------------------
# 2. PERSONEL İÇİN İZİN/RAPOR TALEP FORMU
# --------------------------------------------------------------------------
class LeaveRequestForm(forms.ModelForm):
    """Personelin yeni izin/rapor talebi oluşturması için form."""

    # Doğru girintileme burada başlıyor
    class Meta:
        model = LeaveRequest
        # Formda kullanıcıdan alınacak alanlar
        fields = ['request_type', 'start_date', 'end_date', 'reason']
        labels = { # Alan etiketleri
            'request_type': 'Talep Tipi',
            'start_date': 'Başlangıç Tarihi',
            'end_date': 'Bitiş Tarihi',
            'reason': 'Açıklama / Sebep (İsteğe Bağlı)',
        }
        help_texts = { # Yardımcı metinler
            'start_date': 'İzin veya raporun başlayacağı gün.',
            'end_date': 'İzin veya raporun biteceği gün (bu tarih dahil).',
        }
        # HTML widget'ları
        widgets = {
            # Tarayıcının kendi tarih seçicisini kullanmasını sağla
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # Select ve Textarea için de bootstrap class'ı eklenebilir
            'request_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    # Özel form doğrulama kuralları
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        today = timezone.now().date() # Bugünün tarihi

        # Başlangıç tarihi geçmiş bir tarih olamaz (bugün olabilir)
        if start_date and start_date < today:
            self.add_error('start_date', "Başlangıç tarihi bugünden veya gelecek bir tarihten önce olamaz.")

        # Bitiş tarihi başlangıç tarihinden önce olamaz
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', "Bitiş tarihi başlangıç tarihinden önce olamaz.")

        # Ekstra: Belki maksimum izin süresi kontrolü eklenebilir
        # if start_date and end_date:
        #     duration = (end_date - start_date).days + 1
        #     if duration > 30: # Örnek: 30 günden fazla izin istenemez
        #         self.add_error(None, f"Maksimum izin süresi 30 gündür. ({duration} gün talep edildi).")

        return cleaned_data
    
    # accounts/forms.py (EN ALTA EKLENECEK)

# 3. KULLANICI PROFİL GÜNCELLEME FORMU (Temel Bilgiler)
class UserProfileUpdateForm(forms.ModelForm):
    """Kullanıcının kendi Ad, Soyad ve E-posta bilgilerini güncellemesi için form."""
    class Meta:
        model = User # Django'nun User modelini kullan
        # Sadece bu alanlar düzenlenebilsin
        fields = ['first_name', 'last_name', 'email']
        labels = { # Alan etiketlerini Türkçeleştir
            'first_name': 'Adınız',
            'last_name': 'Soyadınız',
            'email': 'E-posta Adresiniz',
        }
        help_texts = {
            'email': 'İsteğe bağlı. Bildirimler için kullanılabilir.',
        }
        widgets = { # Daha iyi görünüm için input tiplerini belirleyelim
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    # E-posta adresinin benzersiz olup olmadığını kontrol edebiliriz (opsiyonel)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Eğer e-posta girilmişse ve bu e-posta BAŞKA BİR kullanıcıya aitse hata ver
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten başka bir kullanıcı tarafından kullanılıyor.")
        return email