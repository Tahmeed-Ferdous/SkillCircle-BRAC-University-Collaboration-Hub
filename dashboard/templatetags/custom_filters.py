from django import template

register = template.Library()

@register.filter
def dict_key(dictionary, key):
    """
    Safely retrieves a value from a dictionary using a dynamic key.
    """
    return dictionary.get(key, {})
