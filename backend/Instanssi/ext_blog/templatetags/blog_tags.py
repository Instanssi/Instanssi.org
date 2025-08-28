from django import template
from django.core.paginator import Paginator

from Instanssi.ext_blog.models import BlogEntry

register = template.Library()


@register.inclusion_tag("ext_blog/blog_messages.html", takes_context=True)
def render_blog(context, event_id: int, max_posts: int = 10) -> dict:
    request = context["request"]
    page_number = request.GET.get('p', 1) # Default to page 1 if get parameter is missing
    # Make sure the page number from the get parameter is a valid integer:
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1
    full_entries_list = BlogEntry.get_latest().filter(event_id=event_id)
    paginator = Paginator(full_entries_list, max_posts)
    current_page = paginator.get_page(page_number)
    entries = current_page.object_list
    # We will pass this boolean as extra data to the template for simplicity
    # It's used to determine whether to render pagination links or not:
    needs_pagination = paginator.count > paginator.per_page
    return {"entries": entries, "needs_pagination": needs_pagination, "page_range": paginator.page_range, "page_number": current_page.number, "num_pages": paginator.num_pages}
