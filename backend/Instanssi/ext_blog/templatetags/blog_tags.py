from typing import Any

from django import template

from Instanssi.ext_blog.models import BlogEntry

register = template.Library()


@register.inclusion_tag("ext_blog/blog_messages.html")
def render_blog(event_id: int, max_posts: int = 10) -> dict[str, Any]:
    return {"entries": BlogEntry.get_latest().filter(event_id=event_id)[:max_posts]}
