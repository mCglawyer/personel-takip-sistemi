# shift_takip/settings.py (En Güncel ve Tam Hali - 500 Hatası Düzeltildi - 27 Ekim 2025)

"""
Django settings for shift_takip project.
"""

import os
from pathlib import Path
import dj_database_url # Render'ın DATABASE_URL'ini okumak için

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Render'ın "Environment" bölümünden 'DJANGO_SECRET_KEY' olarak ayarlayın.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-yerelde-calisirken-kullanilir')

# SECURITY WARNING: don't run with debug turned on in production!
# Render, 'RENDER' ortam değişkenini otomatik ayarlar. Canlıda False, yerelde True olur.
DEBUG = os.environ.get('RENDER') is None

# İzin verilen alan adları
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]

# Render'ın size verdiği host adlarını otomatik ekle
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Kendi özel alan adlarınızı ekleyin
ALLOWED_HOSTS.extend([
    '127.0.0.1', # Yerel testler için
    'localhost', # Yerel testler için
    'personel-takip-sistemi-yirl.onrender.com', # Render'ın varsayılan adresi
    'www.geekpanel.net',                       # Sizin özel alan adınız
    'geekpanel.net',                           # Kök alan adınız
])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Üçüncü Parti Uygulamalar
    'whitenoise.runserver_nostatic', # DEBUG=True iken whitenoise'un çalışması için
    'pwa',                           # django-pwa paketi
    # Bizim Uygulamalarımız
    'accounts',
    # HATA DÜZELTMESİ: custom_filters buradan SİLİNDİ.
    # Django 'accounts' uygulamasının içindeki 'templatetags' klasörünü otomatik bulur.
]
# HATA DÜZELTMESİ: Bu satır da SİLİNDİ.
# INSTALLED_APPS = [app for app in INSTALLED_APPS if app is not None]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise Middleware (SecurityMiddleware'den hemen sonra gelmeli)
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'], # Proje geneli templates klasörü
        'APP_DIRS': True, # Uygulama klasörlerindeki 'templates' klasörlerini de ara
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # HATA DÜZELTMESİ: 'builtins' bölümü SİLİNDİ veya temizlendi.
            'builtins': [
                # 'accounts.templatetags.custom_filters' ... (BU SATIR SİLİNDİ)
            ],
        },
    },
]
# HATA DÜZELTMESİ: 'builtins' temizleme satırı SİLİNDİ veya içi boşaltıldı.
TEMPLATES[0]['OPTIONS']['builtins'] = [b for b in TEMPLATES[0]['OPTIONS']['builtins'] if b]


WSGI_APPLICATION = 'shift_takip.wsgi.application'


# Database
# Render'daki DATABASE_URL ortam değişkeninden bağlantı bilgilerini okur.
# Bulamazsa (yerel makine), varsayılan olarak SQLite'ı kullanır.
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600 # Bağlantı havuzu ömrü (saniye)
    )
}

# Render'daki PostgreSQL'in SSL bağlantısı gerektirmesi durumunda:
if 'DATABASE_URL' in os.environ: # Sadece canlı ortamda (Render'da)
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require' # PostgreSQL bağlantısını SSL kullanmaya zorla
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
LANGUAGE_CODE = 'tr-TR'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
# Geliştirme sırasında statik dosyaların bulunacağı ek klasörler
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
# CANLI ORTAM İÇİN ZORUNLU: 'collectstatic' komutunun dosyaları toplayacağı yer.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise için Depolama Backend'i (Gerekli)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------------
# E-POSTA AYARLARI
# --------------------------------------------------------------------------
# Canlı ortamda Render Ortam Değişkenleri'nden alınmalı
EMAIL_BACKEND = os.environ.get('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend') # Varsayılan: konsol
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587)) # Port sayı olmalı
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD') # Uygulama şifresi
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

# --------------------------------------------------------------------------
# PWA (Progressive Web App) Ayarları
# --------------------------------------------------------------------------
PWA_APP_NAME = 'Personel Takip Sistemi'
PWA_APP_SHORT_NAME = 'PersonelTakip'
PWA_APP_DESCRIPTION = "Şirket personeli için vardiya ve mola takip sistemi"
PWA_APP_BACKGROUND_COLOR = '#FFFFFF'
PWA_APP_THEME_COLOR = '#007bff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_START_URL = '/'

# İKON YOLLARI (Sizin static/images/icons/ klasörünüzdeki dosya adlarına göre)
PWA_APP_ICONS = [
    {'src': '/static/images/icons/72.png', 'sizes': '72x72'},
    {'src': '/static/images/icons/96.png', 'sizes': '96x96'},
    {'src': '/static/images/icons/128.png', 'sizes': '128x128'},
    {'src': '/static/images/icons/144.png', 'sizes': '144x144'},
    {'src': '/static/images/icons/152.png', 'sizes': '152x152'},
    {'src': '/static/images/icons/192.png', 'sizes': '192x192'},
    {'src': '/static/images/icons/384.png', 'sizes': '384x384'},
    {'src': '/static/images/icons/512.png', 'sizes': '512x512'}
]
PWA_APP_ICONS_APPLE = [
    {'src': '/static/images/icons/180.png', 'sizes': '180x180'}
]

PWA_SERVICE_WORKER_PATH = None  