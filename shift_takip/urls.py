# shift_takip/urls.py (En Güncel ve Tam Hali - PWA Dahil - 23 Ekim 2025)

"""
URL configuration for shift_takip project.

This `urlpatterns` list routes URLs to views. It includes:
- The Django admin site.
- URLs required by the django-pwa package (manifest, serviceworker, offline page) at the root.
- The root URL ('') pointing to the login page.
- All other application URLs prefixed under '/app/', included from accounts.urls.
"""
from django.contrib import admin
# include fonksiyonunu path ile birlikte import ediyoruz
from django.urls import path, include
# Giriş sayfası (ana sayfa) için accounts.views'dan login_view'ı import ediyoruz
from accounts import views as accounts_views

urlpatterns = [
    # 1. Django Admin Paneli -> /admin/
    path('admin/', admin.site.urls),

    # 2. PWA URL'leri -> /, /manifest.json, /serviceworker.js, /offline
    # django-pwa paketinin çalışması için GEREKLİDİR.
    # Projenin kök dizininde olmalı ve genellikle diğer kök path'lerden önce gelmelidir.
    path('', include('pwa.urls')),

    # 3. Giriş Ekranı (Ana Sayfa) -> /
    # Projenin kök URL'i doğrudan giriş sayfasını gösterir.
    # PWA URL'lerinden SONRA gelmesi önemlidir.
    path('', accounts_views.login_view, name='login'),

    # 4. Uygulama URL'leri -> /app/ ile başlayan tüm URL'ler
    # Django, '/app/' ile başlayan bir istek aldığında,
    # kontrolü 'accounts.urls' (yani accounts/urls.py) dosyasına devreder.
    path('app/', include('accounts.urls')),
]