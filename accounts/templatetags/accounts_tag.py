from django import template

register = template.Library()

@register.filter
def splitter(value):
    ls = value[2:-2]
    return ls.split("', '")