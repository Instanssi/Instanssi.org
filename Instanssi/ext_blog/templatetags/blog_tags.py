from django import template
from django.conf import settings

from Instanssi.ext_blog.models import BlogEntry

register = template.Library()


@register.inclusion_tag("ext_blog/blog_messages.html")
def render_blog(event_id, max_posts=10):
    entries = BlogEntry.objects.filter(event_id=int(event_id), public=True).order_by("-date")[:max_posts]
    return {"entries": entries}


@register.inclusion_tag("ext_blog/blog_rss_tag.html")
def render_blog_rss_tag():
    return {}


@register.simple_tag
def blog_rss_url():
    return "http://" + settings.DOMAIN + "/blog/rss/"
