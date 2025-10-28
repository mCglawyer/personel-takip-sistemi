# accounts/models.py (En Güncel ve Tam Hali - Slug Alanı Eklendi - 28 Ekim 2025)

from django.db import models
from django.contrib.auth.models import User # Django'nun hazır Kullanıcı modelini import ediyoruz
from django.utils import timezone
# 'datetime', 'time', 'timedelta' importları Shift modeli için gerekli
from datetime import time, timedelta, datetime
# 'slug' alanı için slugify fonksiyonunu import ediyoruz
from django.utils.text import slugify

# --------------------------------------------------------------------------
# 1. ŞUBE MODELİ (Slug Alanı Eklendi)
# --------------------------------------------------------------------------
class Branch(models.Model):
    """Şirketin farklı şubelerini temsil eder."""
    name = models.CharField(max_length=100, verbose_name="Şube Adı")

    # URL'de kullanılacak benzersiz, 'vadipark-subesi' gibi bir tanımlayıcı
    slug = models.SlugField(
        max_length=120, 
        unique=True,    # Benzersiz olmalı
        blank=True,     # Boş olabilir (biz dolduracağız)
        editable=False  # Admin panelinde görünmesin (otomatik oluşacak)
    )

    def __str__(self):
        return self.name

    # 'save' metodu __str__ ile aynı girinti seviyesinde (sınıfın içinde)
    def save(self, *args, **kwargs):
        """Model kaydedilirken, 'name' alanından slug oluşturur."""

        is_new = self.pk is None # Bu yeni bir şube mi?
        old_name = None
        if not is_new:
            # Eğer eski şubeyse, eski adını al
            # Hata almamak için varlığını kontrol et
            try:
                old_name = Branch.objects.get(pk=self.pk).name
            except Branch.DoesNotExist:
                pass # Henüz veritabanında yoksa (çok nadir bir durum)

        # Sadece YENİ bir şubeyse VEYA slug alanı boşsa VEYA adı değiştiyse
        # yeniden slug oluştur:
        if is_new or not self.slug or self.name != old_name:
            self.slug = slugify(self.name, allow_unicode=True) # Türkçe karakterleri destekle

            # Aynı slug'dan varsa sonuna sayı ekle
            original_slug = self.slug
            counter = 1
            # 'self.pk' kontrolü, objenin zaten var olup olmadığını anlamak için
            while Branch.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1

        super().save(*args, **kwargs) # Asıl kaydetme işlemini yap

# --------------------------------------------------------------------------
# 2. MOLA MODELİ
# --------------------------------------------------------------------------
class Break(models.Model):
    """Personelin aldığı mola kayıtlarını tutar."""
    personnel = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Personel")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, verbose_name="Şube")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Başlangıç Zamanı")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Zamanı")

    def __str__(self):
        status = "Devam Ediyor" if self.end_time is None else "Bitti"
        branch_name = self.branch.name if self.branch else "Bilinmiyor"
        return f"{self.personnel.username} - {branch_name} - {status} ({self.start_time.strftime('%d.%m %H:%M')})"

    @property
    def is_active(self):
        return self.end_time is None

    @property
    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

# --------------------------------------------------------------------------
# 3. VARDİYA TİPLERİ (Sabit Liste)
# --------------------------------------------------------------------------
SHIFT_TYPES = [
    # Normal Vardiyalar (Saatli)
    ('SABAH',   'Sabahçı (07:30 - 16:30)'),
    ('ARACI',   'Aracı (11:30 - 20:30)'),
    ('AKSAM',   'Akşamcı (15:30 - 00:30)'),
    ('ETKINLIK','Etkinlik (Manuel Saat)'),
    ('FAZLA_MESAI', 'Fazla Mesai (Manuel Saat)'), # Fazla mesai eklendi
    # Durumlar (Saatsiz)
    ('IZIN',    'İzinli'),
    ('RAPORLU', 'Raporlu'),
    ('DEVAMSIZ','Devamsız'),
]

# --------------------------------------------------------------------------
# 4. VARDİYA (SHIFT) MODELİ
# --------------------------------------------------------------------------
class Shift(models.Model):
    """Personelin belirli bir gündeki vardiyasını veya durumunu (izin, rapor vb.) temsil eder."""
    personnel = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Personel")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, verbose_name="Şube")
    date = models.DateField(verbose_name="Tarih")
    
    # max_length'i 10'dan 15'e yükseltmiştik
    shift_type = models.CharField(
        max_length=15, 
        choices=SHIFT_TYPES,
        verbose_name="Vardiya Tipi / Durum"
    )

    # Bu alanlar save() metodu tarafından hesaplanır.
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="Vardiya Başlangıç (Hesaplandı)")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Vardiya Bitiş (Hesaplandı)")

    # Sadece 'ETKINLIK' ve 'FAZLA_MESAI' için kullanılır
    custom_start_time = models.TimeField(null=True, blank=True, verbose_name="Manuel Başlangıç Saati")
    custom_end_time = models.TimeField(null=True, blank=True, verbose_name="Manuel Bitiş Saati")

    # Akıllı Kaydetme Fonksiyonu
    def save(self, *args, **kwargs):
        tz = timezone.get_current_timezone()
        self.start_time = None # Saatleri sıfırla
        self.end_time = None

        if self.shift_type == 'SABAH':
            start_dt = datetime.combine(self.date, time(7, 30)); end_dt = datetime.combine(self.date, time(16, 30))
            self.start_time = timezone.make_aware(start_dt, tz); self.end_time = timezone.make_aware(end_dt, tz)
        elif self.shift_type == 'ARACI':
            start_dt = datetime.combine(self.date, time(11, 30)); end_dt = datetime.combine(self.date, time(20, 30))
            self.start_time = timezone.make_aware(start_dt, tz); self.end_time = timezone.make_aware(end_dt, tz)
        elif self.shift_type == 'AKSAM':
            start_dt = datetime.combine(self.date, time(15, 30)); end_date = self.date + timedelta(days=1)
            end_dt = datetime.combine(end_date, time(0, 30))
            self.start_time = timezone.make_aware(start_dt, tz); self.end_time = timezone.make_aware(end_dt, tz)
        
        # 'ETKINLIK' VE 'FAZLA_MESAI' aynı mantığı kullanır
        elif self.shift_type == 'ETKINLIK' or self.shift_type == 'FAZLA_MESAI':
            if self.custom_start_time and self.custom_end_time:
                start_dt = datetime.combine(self.date, self.custom_start_time)
                end_dt = datetime.combine(self.date, self.custom_end_time)
                if self.custom_end_time < self.custom_start_time: # Gece yarısını aşıyor mu?
                     end_date = self.date + timedelta(days=1)
                     end_dt = datetime.combine(end_date, self.custom_end_time)
                self.start_time = timezone.make_aware(start_dt, tz)
                self.end_time = timezone.make_aware(end_dt, tz)

        # 'IZIN', 'RAPORLU', 'DEVAMSIZ' seçilirse, start_time ve end_time None kalır.
        super().save(*args, **kwargs) # Kaydet

    def __str__(self):
        return f"{self.personnel.username} - {self.date.strftime('%d.%m.%Y')} - {self.get_shift_type_display()}"

# --------------------------------------------------------------------------
# 5. PERSONEL PROFİLİ MODELİ
# --------------------------------------------------------------------------
class Profile(models.Model):
    """Django'nun User modeline ek alanlar (örn: atanılan şube) eklemek için kullanılır."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL, # Şube silinirse bu alan boş olur
        null=True, blank=True,
        verbose_name="Atandığı Şube"
    )

    def __str__(self):
        branch_name = self.branch.name if self.branch else "Şube Atanmamış"
        return f"{self.user.username} Profili ({branch_name})"

# --------------------------------------------------------------------------
# 6. İZİN/RAPOR TALEP MODELİ
# --------------------------------------------------------------------------
class LeaveRequest(models.Model):
    """Personelin izin veya rapor taleplerini ve durumlarını tutar."""
    REQUEST_TYPES = [ ('IZIN', 'Yıllık İzin / Ücretsiz İzin'), ('RAPOR', 'Sağlık Raporu'), ]
    STATUS_CHOICES = [ ('BEKLIYOR', 'Onay Bekliyor'), ('ONAYLANDI', 'Onaylandı'), ('REDDEDILDI', 'Reddedildi'), ]

    personnel = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Talep Eden Personel")
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPES, verbose_name="Talep Tipi")
    start_date = models.DateField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateField(verbose_name="Bitiş Tarihi")
    reason = models.TextField(blank=True, verbose_name="Açıklama / Sebep")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='BEKLIYOR', verbose_name="Talep Durumu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Zamanı")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="İşlem Zamanı")
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='processed_leave_requests',
        verbose_name="İşlemi Yapan Yönetici"
    )
    manager_notes = models.TextField(blank=True, verbose_name="Yönetici Notu")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "İzin/Rapor Talebi"
        verbose_name_plural = "İzin/Rapor Talepleri"

    def __str__(self):
        return f"{self.personnel.username} - {self.get_request_type_display()} ({self.start_date.strftime('%d.%m')} - {self.end_date.strftime('%d.%m')}) - {self.get_status_display()}"

    @property
    def duration_days(self):
        if self.end_date >= self.start_date:
            return (self.end_date - self.start_date).days + 1
        return 0