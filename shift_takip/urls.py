# shift_takip/urls.py (DÜZELTİLMİŞ VE TEMİZ HALİ)

from django.contrib import admin
from django.urls import path, include # 'include' import edilmiş olmalı
from accounts import views as accounts_views # 'login_view' için bu gerekli

urlpatterns = [
    # 1. Django Admin Paneli
    path('admin/', admin.site.urls),

    # 2. PWA URL'leri (serviceworker.js, manifest.json vb. için)
    # BU, login_view'dan ÖNCE gelmeli
    path('', include('pwa.urls')),

    # 3. Giriş Ekranı (Ana Sayfa)
    # Kök URL ('') için ana giriş sayfamız
    path('', accounts_views.login_view, name='login'),

    # 4. Uygulama URL'leri (/app/ altında)
    # Diğer tüm sayfalar (dashboard, mola, profil vb.)
    path('app/', include('accounts.urls')),
]