# -*- coding: utf-8 -*-

from django import template
register = template.Library()
import hashlib

@register.simple_tag
def gravatar_url(email):
    return 'https://www.gravatar.com/avatar/'+hashlib.md5(email.lower()).hexdigest()+'?d=retro'