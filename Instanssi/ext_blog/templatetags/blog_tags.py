# -*- coding: utf-8 -*-

from django import template
from Instanssi.ext_blog.models import BlogEntry

register = template.Library()

@register.inclusion_tag('ext_blog/blog_messages.html')
def render_blog(event_id):
    entries = BlogEntry.objects.filter(event_id__lte=int(event_id), public=True)[:10]
    return {'entries': entries}

@register.inclusion_tag('ext_blog/blog_rss_tag.html')
def render_blog_rss_tag():
    return {}

@register.simple_tag
def blog_rss_url():
    return 'http://instanssi.org/blog/rss/'

