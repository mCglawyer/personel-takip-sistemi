# accounts/admin.py
from django.contrib import admin
from .models import Branch, Break, Shift 
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Branch, Break, Shift, Profile
from .models import Branch, Break, Shift, Profile, LeaveRequest

admin.site.register(Branch)
admin.site.register(Break)
admin.site.register(Shift) 


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False # Profili user'dan ayrı silmeyi engelle
    verbose_name_plural = 'Personel Profili'
    fk_name = 'user' # İlişkiyi belirt

# Mevcut UserAdmin'i genişleterek ProfileInline'ı ekleyelim
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_branch') # Şubeyi listede göster
    list_select_related = ('profile', 'profile__branch') # Performans için

    # Şube bilgisini getiren fonksiyon
    def get_branch(self, instance):
        if hasattr(instance, 'profile') and instance.profile.branch:
            return instance.profile.branch.name
        return "Atanmamış"
    get_branch.short_description = 'Atandığı Şube' # Sütun başlığı

# Mevcut User admin kaydını kaldırıp yenisini (Custom) kaydedelim
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'personnel',
        'request_type',
        'start_date',
        'end_date',
        'status',
        'created_at',
        'processed_by'
    )
    list_filter = ('status', 'request_type', 'personnel__profile__branch', 'start_date') # Şubeye göre filtre ekleyelim
    search_fields = ('personnel__username', 'personnel__first_name', 'personnel__last_name')
    # Sadece okunabilir alanlar (eğer admin panelinden değiştirilmesin istiyorsak)
    # readonly_fields = ('created_at', 'processed_at', 'processed_by')

    # Admin panelinde onay/red işlemini kolaylaştırmak için action eklenebilir (İleri seviye)
    # actions = ['approve_requests', 'reject_requests']

    # def approve_requests(self, request, queryset):
    #     queryset.update(status='ONAYLANDI', processed_by=request.user, processed_at=timezone.now())
    # approve_requests.short_description = "Seçili talepleri ONAYLA"

    # def reject_requests(self, request, queryset):
    #     queryset.update(status='REDDEDILDI', processed_by=request.user, processed_at=timezone.now())
    # reject_requests.short_description = "Seçili talepleri REDDET"

# Profile modelini User adminine bağlayan kodlar (önceden vardı)
# class ProfileInline(admin.StackedInline): ...
# class CustomUserAdmin(BaseUserAdmin): ...
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)

# Diğer modeller (önceden vardı)
# admin.site.register(Branch)
# admin.site.register(Break)
# # ShiftAdmin zaten @admin.register ile kaydedilmişti