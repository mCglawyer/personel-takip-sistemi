# accounts/templatetags/custom_filters.py (Düzeltilmiş Hali)
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Allows accessing dictionary keys with variables in templates.
    Handles None input gracefully.
    """
    # ÖNEMLİ: Eğer gelen 'dictionary' gerçekten bir sözlük değilse
    # (örneğin bir önceki filtreden None geldiyse), hata verme, None döndür.
    if not isinstance(dictionary, dict):
        return None

    # Anahtar (key) tamsayı ise (örn: user.id), string'e çevir
    # Çünkü views.py'da shifts_map'i string ID ile oluşturduk.
    if isinstance(key, int):
        key = str(key)

    # Sözlükten anahtarı .get() ile al. Anahtar yoksa None döner.
    return dictionary.get(key)

# Not: İkinci bir filtreye (get_item_nested) gerek yok.
# Aynı filtre zincirleme (pipe |) ile kullanıldığında bu kontrol yeterlidir.

# accounts/templatetags/custom_filters.py (EN ALTA EKLENECEK)

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Checks if a user belongs to a specific group.
    Usage: {% if user|has_group:"Group Name" %}
    """
    # Kullanıcının üye olduğu grupların isimlerini al ve kontrol et
    return user.groups.filter(name=group_name).exists()