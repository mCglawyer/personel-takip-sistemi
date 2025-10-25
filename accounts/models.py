# accounts/models.py (En Güncel ve Tam Hali)

from django.db import models
from django.contrib.auth.models import User # Django'nun hazır Kullanıcı modelini import ediyoruz
from django.utils import timezone
# 'datetime', 'time', 'timedelta' importları Shift modeli için gerekli
from datetime import time, timedelta, datetime

# --------------------------------------------------------------------------
# 1. ŞUBE MODELİ
# --------------------------------------------------------------------------
class Branch(models.Model):
    """Şirketin farklı şubelerini temsil eder."""
    name = models.CharField(max_length=100, verbose_name="Şube Adı")
    # Gelecekte adres, telefon vb. eklenebilir

    def __str__(self):
        return self.name

# --------------------------------------------------------------------------
# 2. MOLA MODELİ
# --------------------------------------------------------------------------
class Break(models.Model):
    """Personelin aldığı mola kayıtlarını tutar."""
    personnel = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Personel")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, verbose_name="Şube")
    # Mola başlangıcı: Kayıt oluşturulduğunda otomatik olarak o anki zamanı alır
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Başlangıç Zamanı")
    # Mola bitişi: Mola bitince doldurulur, başta boştur (null=True)
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Zamanı")

    def __str__(self):
        """Admin panelinde ve loglarda daha okunaklı gösterim sağlar."""
        status = "Devam Ediyor" if self.end_time is None else "Bitti"
        branch_name = self.branch.name if self.branch else "Bilinmiyor"
        return f"{self.personnel.username} - {branch_name} - {status} ({self.start_time.strftime('%d.%m %H:%M')})"

    @property
    def is_active(self):
        """Bu mola kaydının hala aktif (bitmemiş) olup olmadığını kontrol eder."""
        return self.end_time is None

    @property
    def duration(self):
        """Molannın süresini hesaplar (eğer bitmişse)."""
        if self.end_time:
            return self.end_time - self.start_time
        return None # Mola hala devam ediyorsa süre hesaplanamaz

# --------------------------------------------------------------------------
# 3. VARDİYA TİPLERİ (Sabit Liste)
# --------------------------------------------------------------------------
# Bu liste hem Shift modelinde 'choices' olarak hem de views.py'da kullanılır.
# Class dışına taşındı (ImportError çözümü için).
SHIFT_TYPES = [
    # Normal Vardiyalar (Saatli)
    ('SABAH',   'Sabahçı (07:30 - 16:30)'),
    ('ARACI',   'Aracı (11:30 - 20:30)'),
    ('AKSAM',   'Akşamcı (15:30 - 00:30)'),
    ('ETKINLIK','Etkinlik (Manuel Saat)'),
    ('FAZLA_MESAI', 'Fazla Mesai (Manuel Saat)'),
    # Durumlar (Saatsiz)
    ('IZIN',    'İzinli'),
    ('RAPORLU', 'Raporlu'),    # Yeni eklendi
    ('DEVAMSIZ','Devamsız'),   # Yeni eklendi
]

# --------------------------------------------------------------------------
# 4. VARDİYA (SHIFT) MODELİ (Akıllı Hesaplama Yapan Versiyon)
# --------------------------------------------------------------------------
class Shift(models.Model):
    """Personelin belirli bir gündeki vardiyasını veya durumunu (izin, rapor vb.) temsil eder."""
    personnel = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Personel")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, verbose_name="Şube")
    # Vardiyanın veya durumun geçerli olduğu gün
    date = models.DateField(verbose_name="Tarih")
    # Seçilen vardiya tipi veya durumu (yukarıdaki SHIFT_TYPES listesinden)
    shift_type = models.CharField(
        max_length=10,
        choices=SHIFT_TYPES,
        verbose_name="Vardiya Tipi / Durum"
    )

    # Bu alanlar doğrudan girilmez, aşağıdaki save() metodu tarafından hesaplanır.
    # 'IZIN', 'RAPORLU', 'DEVAMSIZ' durumlarında boş (None) kalırlar.
    start_time = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Vardiya Başlangıç (Hesaplandı)"
    )
    end_time = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Vardiya Bitiş (Hesaplandı)"
    )

    # Sadece 'ETKINLIK' tipi seçildiğinde manuel saat girişi için kullanılır.
    custom_start_time = models.TimeField(null=True, blank=True, verbose_name="Etkinlik Başlangıç Saati")
    custom_end_time = models.TimeField(null=True, blank=True, verbose_name="Etkinlik Bitiş Saati")

   # accounts/models.py -> Shift modelinin içindeki save fonksiyonu

# Akıllı Kaydetme Fonksiyonu
def save(self, *args, **kwargs):
    # Admin 'Kaydet'e bastığında bu fonksiyon çalışacak
    tz = timezone.get_current_timezone()
    self.start_time = None # Önce saatleri sıfırla
    self.end_time = None

    if self.shift_type == 'SABAH':
        start_dt = datetime.combine(self.date, time(7, 30))
        end_dt = datetime.combine(self.date, time(16, 30))
        self.start_time = timezone.make_aware(start_dt, tz)
        self.end_time = timezone.make_aware(end_dt, tz)

    elif self.shift_type == 'ARACI':
        start_dt = datetime.combine(self.date, time(11, 30))
        end_dt = datetime.combine(self.date, time(20, 30))
        self.start_time = timezone.make_aware(start_dt, tz)
        self.end_time = timezone.make_aware(end_dt, tz)

    elif self.shift_type == 'AKSAM':
        start_dt = datetime.combine(self.date, time(15, 30))
        end_date = self.date + timedelta(days=1) # Gece yarısını aşıyor
        end_dt = datetime.combine(end_date, time(0, 30))
        self.start_time = timezone.make_aware(start_dt, tz)
        self.end_time = timezone.make_aware(end_dt, tz)

    # HATA MUHTEMELEN BURADAYDI:
    # Bu 'elif' bloğundan sonraki 'if' bloğu 4 boşluk içeride olmalı.
    elif self.shift_type == 'ETKINLIK' or self.shift_type == 'FAZLA_MESAI':
        # --- BU BLOK İÇERİDE OLMALI ---
        if self.custom_start_time and self.custom_end_time:
            start_dt = datetime.combine(self.date, self.custom_start_time)
            end_dt = datetime.combine(self.date, self.custom_end_time)

            if self.custom_end_time < self.custom_start_time: # Gece yarısını aşıyor mu?
                 end_date = self.date + timedelta(days=1)
                 end_dt = datetime.combine(end_date, self.custom_end_time)

            self.start_time = timezone.make_aware(start_dt, tz)
            self.end_time = timezone.make_aware(end_dt, tz)
        # --- GIRINTILI BLOK SONU ---

    # 'IZIN', 'RAPORLU', 'DEVAMSIZ' seçilirse, start_time ve end_time None kalır.

    super().save(*args, **kwargs) # Değişiklikleri veritabanına kaydet

    def __str__(self):
        """Admin panelinde daha okunaklı gösterim."""
        # get_shift_type_display() -> choices listesindeki okunabilir metni (örn: 'Sabahçı (...)') alır
        return f"{self.personnel.username} - {self.date.strftime('%d.%m.%Y')} - {self.get_shift_type_display()}"

# --------------------------------------------------------------------------
# 5. PERSONEL PROFİLİ MODELİ
# --------------------------------------------------------------------------
class Profile(models.Model):
    """Django'nun User modeline ek alanlar (örn: atanılan şube) eklemek için kullanılır."""
    # Her User için sadece bir Profile olabilir (OneToOneField)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Personelin normalde çalıştığı/atanmış olduğu şube
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL, # Şube silinirse bu alan boş olur
        null=True, blank=True,    # Boş olabilir
        verbose_name="Atandığı Şube"
    )
    # Gelecekte telefon, departman vb. eklenebilir

    def __str__(self):
        branch_name = self.branch.name if self.branch else "Şube Atanmamış"
        return f"{self.user.username} Profili ({branch_name})"

# Opsiyonel: User oluşturulduğunda otomatik Profile oluşturma sinyali
# Bunu etkinleştirmek için en üste importları ekleyin:
# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     """Yeni bir User oluşturulduğunda veya güncellendiğinde Profile'ı da yönetir."""
#     if created:
#         Profile.objects.get_or_create(user=instance) # Varsa al, yoksa oluştur
#     # Her User save işleminde Profile'ı da kaydet (güncellemeler için)
#     # Bu satır bazen gereksiz olabilir veya döngüye yol açabilir, dikkatli kullanılmalı.
#     # instance.profile.save()

class LeaveRequest(models.Model):
    """Personelin izin veya rapor taleplerini ve durumlarını tutar."""

    # Talep Tipleri
    REQUEST_TYPES = [
        ('IZIN', 'Yıllık İzin / Ücretsiz İzin'),
        ('RAPOR', 'Sağlık Raporu'),
        # Gelecekte başka tipler eklenebilir (örn: Doğum İzni)
    ]

    # Talep Durumları
    STATUS_CHOICES = [
        ('BEKLIYOR', 'Onay Bekliyor'),
        ('ONAYLANDI', 'Onaylandı'),
        ('REDDEDILDI', 'Reddedildi'),
    ]

    # Model Alanları
    personnel = models.ForeignKey(
        User,
        on_delete=models.CASCADE, # Kullanıcı silinirse talepleri de silinsin
        verbose_name="Talep Eden Personel"
    )
    request_type = models.CharField(
        max_length=10,
        choices=REQUEST_TYPES,
        verbose_name="Talep Tipi"
    )
    start_date = models.DateField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateField(verbose_name="Bitiş Tarihi")
    reason = models.TextField(
        blank=True, # Sebep girmek isteğe bağlı olsun
        verbose_name="Açıklama / Sebep"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='BEKLIYOR', # Varsayılan durum
        verbose_name="Talep Durumu"
    )
    # Talep ne zaman oluşturuldu? (Otomatik)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Zamanı")
    # Talep ne zaman işlendi (onay/red)? (Yönetici işlem yapınca güncellenecek)
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="İşlem Zamanı")
    # İşlemi yapan yönetici kim? (Boş olabilir)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, # Yönetici silinirse kayıt kalır, bu alan boş olur
        null=True, blank=True,
        related_name='processed_leave_requests', # User'dan taleplere erişim için
        verbose_name="İşlemi Yapan Yönetici"
    )
    # Yöneticinin reddetme veya onaylama notu (isteğe bağlı)
    manager_notes = models.TextField(blank=True, verbose_name="Yönetici Notu")

    class Meta:
        # Talepleri en yeniden eskiye sıralayalım
        ordering = ['-created_at']
        verbose_name = "İzin/Rapor Talebi"
        verbose_name_plural = "İzin/Rapor Talepleri"

    def __str__(self):
        return f"{self.personnel.username} - {self.get_request_type_display()} ({self.start_date.strftime('%d.%m')} - {self.end_date.strftime('%d.%m')}) - {self.get_status_display()}"

    # Talep süresini hesaplayan bir property ekleyebiliriz (isteğe bağlı)
    @property
    def duration_days(self):
        # Bitiş tarihi başlangıçtan büyük veya eşit olmalı
        if self.end_date >= self.start_date:
            # İki tarih arasındaki fark + 1 gün (örn: aynı gün ise 1 gün)
            return (self.end_date - self.start_date).days + 1
        return 0 # Hatalı tarih aralığı