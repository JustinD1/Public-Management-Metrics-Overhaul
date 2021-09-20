from django import template

register = template.Library()

@register.simple_tag
def get_item(dictionary,key,key_2):
    if (key is None) or (key_2 is None):
        return False
    first = dictionary.get(key)
    second = first.get(key_2)
    return second
