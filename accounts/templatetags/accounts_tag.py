from django import template
import datetime
from django.utils import timezone

register = template.Library()

@register.filter
def splitter(value):
    ls = value[2:-2]
    return ls.split("', '")

def timer(value):
    time_now = timezone.now()
    total_secs = (time_now - value).total_seconds()
    return total_secs/3600