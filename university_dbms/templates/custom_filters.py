# university_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary is None:
        return None
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    if hasattr(dictionary, '__getitem__'):
        try:
            return dictionary[key]
        except (KeyError, IndexError, TypeError):
            return None
    return None

@register.filter
def replace(value, arg):
    """Replace all occurrences of arg in string"""
    if not value:
        return value
    if ',' not in str(arg):
        return value
    old, new = str(arg).split(',', 1)
    return str(value).replace(old, new)
