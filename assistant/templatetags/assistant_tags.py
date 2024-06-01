from django import template
from django.conf import settings
import json

register = template.Library()

from assistant.models import *

@register.filter
def get_first_four_words(value):
    if value is not None:
        words = value.split()[:4]
        if len(value.split()) > 4:
            return ' '.join(words) + ' ...'
        else:
            return ' '.join(words)
    else:
        return None
    
@register.filter
def image_tag(image_url):
    return f'<img src="{image_url}" alt="Image">'

@register.filter
def json_tag(value):
    return json.loads(value)

@register.filter
def get_first_n_words(value, n=4):
    words = value.split()
    if len(words) > n:
        return ' '.join(words[:n]) + '...'
    return value