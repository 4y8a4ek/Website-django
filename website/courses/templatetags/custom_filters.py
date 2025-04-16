# custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Возвращает значение по ключу в словаре"""
    return dictionary.get(str(key), None)

@register.filter
def get_item_test(value, index):
    """Получает элемент списка по индексу."""
    try:
        return value[int(index)]  # Преобразуем индекс в целое число и получаем элемент
    except (IndexError, ValueError):
        return None 
    
@register.filter
def index(sequence, i):
    try:
        return sequence[int(i)]
    except:
        return ''