from django import template

register = template.Library()

@register.filter
def kategori_color(kategori):
    """Mengembalikan kelas CSS berdasarkan kategori kondisi"""
    if kategori == 'SESUAI':
        return 'bg-green-100 text-green-800'
    elif kategori == 'KT_MINOR':
        return 'bg-yellow-100 text-yellow-800'
    elif kategori == 'KT_MAYOR':
        return 'bg-red-100 text-red-800'
    return 'bg-gray-100 text-gray-800'

@register.filter
def kategori_icon(kategori):
    """Mengembalikan ikon berdasarkan kategori kondisi"""
    if kategori == 'SESUAI':
        return 'fas fa-check-circle'
    elif kategori == 'KT_MINOR':
        return 'fas fa-exclamation-triangle'
    elif kategori == 'KT_MAYOR':
        return 'fas fa-times-circle'
    return 'fas fa-info-circle'