# -*- coding: utf-8 -*-

from django import template
from Instanssi.ext_blog.models import BlogEntry

register = template.Library()

@register.inclusion_tag('ext_blog/blog_messages.html')
def render_blog(event_id):
    entries = BlogEntry.objects.filter(event_id=int(event_id), public=True)
    return {'entries': entries}

@register.inclusion_tag('ext_blog/blog_rss_tag.html')
def render_blog_rss_tag(event_id):
    return {'event_id': event_id}