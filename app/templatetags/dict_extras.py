from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    dictionary = dict(dictionary)
    return dictionary.get(key)
