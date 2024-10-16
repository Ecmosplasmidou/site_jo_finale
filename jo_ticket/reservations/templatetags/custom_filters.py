from django import template
from datetime import timedelta, datetime

register = template.Library()

@register.filter
def add_hours(value, hours):
    if isinstance(value, datetime):
        return value + timedelta(hours=hours)
    return value