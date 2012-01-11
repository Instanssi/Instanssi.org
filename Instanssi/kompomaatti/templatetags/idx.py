# -*- coding: utf-8 -*-

from django import template
register = template.Library()

@register.filter
def idx(h, key):
    return h[key]
