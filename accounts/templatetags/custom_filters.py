# accounts/templatetags/custom_filters.py

from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Kullanıcının belirli bir grupta olup olmadığını kontrol eder.
    Kullanım: {% if user|has_group:"Grup Adı" %}
    """
    # Superuser her zaman True döndürsün (veya gruplarını kontrol etsin)
    if user.is_superuser:
        # return True # Superuser'ı her zaman yetkili say
        pass # Veya superuser'ın da grupta olmasını zorunlu kıl (mevcut mantık)

    return user.groups.filter(name=group_name).exists()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template içinde sözlükten değişkene göre anahtar almayı sağlar.
    (weekly_schedule.html için gerekiyordu)
    """
    if not isinstance(dictionary, dict):
        return None
    if isinstance(key, int): # Anahtar sayıysa string'e çevir
        key = str(key)
    return dictionary.get(key)