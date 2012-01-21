# -*- coding: utf-8 -*-

from django import template
from datetime import datetime
register = template.Library()

@register.filter
def is_editable(entry):
    return (entry.compo.editing_end > datetime.now())
    
