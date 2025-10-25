# shift_takip/settings.py (En Güncel ve Tam Hali - PWA İkon Yolları Düzeltildi - 23 Ekim 2025)

"""
Django settings for shift_takip project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# GERÇEK PROJEDE BU ANAHTARI GÜVENLİ BİR YERDE SAKLAYIN (örn: environment variable)
SECRET_KEY = 'django-insecure-=gizli_anahtar_buraya=)uf*s%7&^c' # Örnek, sizdeki farklıdır

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # Geliştirme için True, Canlıya alırken False yapılmalı!

# Canlıya alırken buraya alan adlarınızı eklemelisiniz. Örn: ['www.siteadi.com', 'siteadi.com']
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.1.104','personel-takip-sistemi-yirl.onrender.com']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Bizim Uygulamalarımız
    'accounts',         # Personel, Mola, Vardiya, Talep vb. modellerinin olduğu uygulama
    'pwa',              # django-pwa paketi
    # Özel template filtreleri için (templatetags klasörü varsa)
    'accounts.templatetags.custom_filters' if os.path.isdir(BASE_DIR / 'accounts/templatetags') else None,
]
# None olanları listeden temizle (eğer templatetags yoksa hata vermesin)
INSTALLED_APPS = [app for app in INSTALLED_APPS if app is not None]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shift_takip.urls' # Ana URL yapılandırma dosyamız

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Proje genelindeki 'templates' klasörünü Django'ya tanıtıyoruz
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True, # Uygulama klasörlerindeki 'templates' klasörlerini de ara
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # Özel template filtrelerini yüklemek için (eğer varsa)
            'builtins': [
                'accounts.templatetags.custom_filters' if 'accounts.templatetags.custom_filters' in INSTALLED_APPS else '',
            ],
        },
    },
]
# None/Boş olanları builtins'den temizle
TEMPLATES[0]['OPTIONS']['builtins'] = [b for b in TEMPLATES[0]['OPTIONS']['builtins'] if b]


WSGI_APPLICATION = 'shift_takip.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
# Geliştirme için SQLite kullanıyoruz. Canlıda PostgreSQL veya MySQL tercih edilir.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'tr-TR' # Dil kodunu Türkçe yaptık

TIME_ZONE = 'Europe/Istanbul' # Saat dilimini Türkiye olarak ayarladık

USE_I18N = True # Uluslararasılaştırmayı etkinleştir (Dil çevirileri için)

USE_TZ = True # Saat dilimi desteğini etkinleştir


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/' # Statik dosyaların tarayıcıda hangi URL altında sunulacağı

# Geliştirme sırasında statik dosyaların bulunacağı ek klasörler
STATICFILES_DIRS = [
    BASE_DIR / 'static', # Proje genelindeki 'static' klasörü
]

# Canlıya alırken 'collectstatic' komutunun dosyaları toplayacağı klasör (DEBUG=False iken gerekli)
# STATIC_ROOT = BASE_DIR / 'staticfiles_production'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------------
# E-POSTA AYARLARI
# --------------------------------------------------------------------------

# Geliştirme için: E-postaları göndermek yerine konsola yazdır.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'webmaster@localhost' # Konsol backend için varsayılan gönderici

# Canlıya alındığında gerçek SMTP ayarları buraya gelecek
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@example.com'
# EMAIL_HOST_PASSWORD = 'your-email-password-or-app-password'
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# --------------------------------------------------------------------------
# PWA (Progressive Web App) Ayarları (django-pwa paketi için)
# --------------------------------------------------------------------------

PWA_APP_NAME = 'Personel Takip Sistemi'
PWA_APP_SHORT_NAME = 'PersonelTakip'
PWA_APP_DESCRIPTION = "Şirket personeli için vardiya ve mola takip sistemi"
PWA_APP_BACKGROUND_COLOR = '#FFFFFF'
PWA_APP_THEME_COLOR = '#007bff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_START_URL = '/' # Ana sayfaya (giriş ekranı) yönlendirsin
# PWA_APP_ORIENTATION = 'any'

# İKON YOLLARI KONTROL EDİLDİ VE GÜNCELLENDİ (Sizin klasör yapınıza göre)
# static/images/icons/ KLASÖRÜNDEKİ GERÇEK DOSYA ADLARIYLA EŞLEŞTİRİLDİ
PWA_APP_ICONS = [
    # Bu boyutların klasörünüzde olduğundan emin olun!
    {'src': '/static/images/icons/72.png', 'sizes': '72x72'},    # Eğer 72.png varsa
    {'src': '/static/images/icons/96.png', 'sizes': '96x96'},    # Eğer 96.png varsa
    {'src': '/static/images/icons/128.png', 'sizes': '128x128'},   # Bu vardı
    {'src': '/static/images/icons/144.png', 'sizes': '144x144'},   # Bu vardı
    {'src': '/static/images/icons/152.png', 'sizes': '152x152'},   # Bu vardı
    {'src': '/static/images/icons/192.png', 'sizes': '192x192'},   # 192.png olmalı!
    {'src': '/static/images/icons/384.png', 'sizes': '384x384'},   # 384.png olmalı!
    {'src': '/static/images/icons/512.png', 'sizes': '512x512'}    # 512.png olmalı!
]
PWA_APP_ICONS_APPLE = [
    # Apple ikonu için de doğru dosya adını kontrol edin (örn: apple-touch-icon.png veya 180.png)
    {'src': '/static/images/icons/180.png', 'sizes': '180x180'} # Örnek, sizdeki farklıysa değiştirin
]
