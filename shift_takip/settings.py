# shift_takip/settings.py (En Güncel ve Tam Hali - Render Dağıtımı İçin Hazır - 25 Ekim 2025)

"""
Django settings for shift_takip project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# CANLI ORTAMDA BUNU MUTLAKA ORTAM DEĞİŞKENİNDEN ALIN!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-=varsayilan_ama_degistir=)uf*s%7&^c') # Örnek

# SECURITY WARNING: don't run with debug turned on in production!
# Render genellikle 'RENDER' ortam değişkenini ayarlar.
# Canlıda otomatik False, yerelde True yapar.
DEBUG = os.environ.get('RENDER') is None

# İzin verilen alan adları
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'personel-takip-sistemi-yirl.onrender.com', # Render'ın varsayılan adresi
    'www.geekpanel.net',                       # Sizin özel alan adınız
    'geekpanel.net',                           # Kök alan adınız
]

# Render'ın kendi dahili host adını da eklemek gerekebilir (Opsiyonel, hata alırsanız eklersiniz)
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Üçüncü Parti Uygulamalar
    'whitenoise.runserver_nostatic', # DEBUG=True iken whitenoise'un çalışması için (runserver ile)
    'pwa',                           # django-pwa paketi
    # Bizim Uygulamalarımız
    'accounts',
    # Özel template filtreleri için (templatetags klasörü varsa)
    'accounts.templatetags.custom_filters' if os.path.isdir(BASE_DIR / 'accounts/templatetags') else None,
]
INSTALLED_APPS = [app for app in INSTALLED_APPS if app is not None]

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

ROOT_URLCONF = 'shift_takip.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Proje geneli templates klasörü
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [
                'accounts.templatetags.custom_filters' if 'accounts.templatetags.custom_filters' in INSTALLED_APPS else '',
            ],
        },
    },
]
TEMPLATES[0]['OPTIONS']['builtins'] = [b for b in TEMPLATES[0]['OPTIONS']['builtins'] if b]


WSGI_APPLICATION = 'shift_takip.wsgi.application'


# Database
# Render için ortam değişkeninden okumak en iyisidir.
# `dj-database-url` paketini kurup kullanmak tavsiye edilir.
# pip install dj-database-url
# import dj_database_url

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        # --- RENDER POSTGRESQL ÖRNEĞİ (Yorumda - Ortam değişkeni daha iyi) ---
        # Veritabanı URL'sini Render Environment bölümünden DATABASE_URL olarak ayarlayın.
        # 'default': dj_database_url.config(
        #     default=f'sqlite:///{BASE_DIR / "db.sqlite3"}', # Yerel için fallback
        #     conn_max_age=600 # Bağlantı havuzu ömrü (saniye)
        # )
        # Manuel ayar (Ortam değişkeni yoksa):
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'render_db_adı',
        # 'USER': 'render_kullanıcı_adı',
        # 'PASSWORD': 'render_db_sifresi',
        # 'HOST': 'render_db_host_adresi.oregon-postgres.render.com',
        # 'PORT': '5432',
    }
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
# Render'daki 'Static Files' -> 'Publish directory' ayarıyla eşleşmeli.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise için Depolama Backend'i (Önerilen)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------------
# E-POSTA AYARLARI
# --------------------------------------------------------------------------
# Canlı ortamda Render Ortam Değişkenleri'nden alınmalı
EMAIL_BACKEND = os.environ.get('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend') # Varsayılan: konsol
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25)) # Port sayı olmalı
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'False').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '') # Uygulama şifresi
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

# İKON YOLLARI KONTROL EDİLDİ VE GÜNCELLENDİ (Sizin klasör yapınıza göre)
# static/images/icons/ KLASÖRÜNDEKİ GERÇEK DOSYA ADLARIYLA EŞLEŞTİRİLDİ
PWA_APP_ICONS = [
    # Bu boyutların 'static/images/icons/' klasöründe olduğundan emin olun!
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
    # Apple ikonu için de doğru dosya adını kontrol edin
    {'src': '/static/images/icons/180.png', 'sizes': '180x180'} # Örnek, sizdeki farklıysa değiştirin
]
# PWA_APP_SPLASH_SCREEN = [...]