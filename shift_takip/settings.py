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
# GERÇEK PROJEDE BU ANAHTARI GÜVENLİ BİR YERDE SAKLAYIN (örn: environment variable)
SECRET_KEY = 'django-insecure-=gizli_anahtar_buraya=)uf*s%7&^c' # Örnek, sizdeki farklıdır

# SECURITY WARNING: don't run with debug turned on in production!
# Render gibi platformlar genellikle bu ayarı ortam değişkeniyle yönetir.
# Yerelde True, Canlıda False olmalı. Şimdilik True bırakabiliriz,
# ama ALLOWED_HOSTS'u ayarlamak önemlidir.
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'https://personel-takip-sistemi-yirl.onrender.com/', # BU SATIRIN EKLENDİĞİNDEN EMİN OLUN
    # Eğer özel alan adınız varsa o da burada olmalı
]


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
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
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
# CANLI ORTAMDA (Render) PostgreSQL/MySQL kullanılmalı.
# PythonAnywhere adımında eklediğimiz DB ayarlarını Render için de uyarlamanız gerekir.
# Şimdilik yerel SQLite ayarı duruyor. Render'a dağıtım yaparken
# Render'ın Databases bölümünden aldığınız bilgilerle burayı güncellemelisiniz.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        # --- RENDER POSTGRESQL ÖRNEĞİ (Yorumda) ---
        # Render, veritabanı bağlantı bilgisini genellikle DATABASE_URL
        # adında bir ortam değişkeni olarak verir. django-environ gibi bir
        # paketle bunu okumak daha iyidir ama manuel olarak da eklenebilir.
        # DİKKAT: Render'da veritabanı oluşturduktan sonra bu bilgileri girin.
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'render_db_adı',
        # 'USER': 'render_kullanıcı_adı',
        # 'PASSWORD': 'render_db_sifresi',
        # 'HOST': 'render_db_host_adresi.oregon-postgres.render.com', # Örnek
        # 'PORT': '5432', # Genellikle standart port
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
    BASE_DIR / 'static', # Proje geneli static klasörü
]
# CANLI ORTAM İÇİN ZORUNLU: 'collectstatic' komutunun dosyaları toplayacağı yer.
# Render'daki 'Static Files' -> 'Publish directory' ayarıyla eşleşmeli.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise için (DEBUG=False iken statik dosyaları sunmaya yardımcı olur - opsiyonel)
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------------
# E-POSTA AYARLARI
# --------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Geliştirme için konsol
DEFAULT_FROM_EMAIL = 'webmaster@localhost'
# Canlı ayarları yorumda
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# ... (Diğer SMTP ayarları Render'da Ortam Değişkeni olarak ayarlanabilir) ...

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
    # Apple ikonu için de doğru dosya adını kontrol edin (örn: apple-touch-icon.png veya 180.png)
    {'src': '/static/images/icons/180.png', 'sizes': '180x180'} # Örnek, sizdeki farklıysa değiştirin
]
# PWA_APP_SPLASH_SCREEN = [...] # İsteğe bağlı
# PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'static/js', 'serviceworker.js') # Özel SW için