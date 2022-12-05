from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404

from Instanssi.ext_blog.models import BlogEntry
from Instanssi.kompomaatti.models import Event


class BlogFeedAll(Feed):
    title = "Instanssi.org Blogi"
    link = "http://instanssi.org"
    description = "Instanssi-demopartyn uusimmat uutiset."

    def items(self):
        entries = []
        for entry in BlogEntry.objects.filter(public=True).order_by("-date")[:25]:
            entry.event_url = entry.event.mainurl
            entries.append(entry)
        return entries

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text

    def item_link(self, item):
        return f"{item.event_url}#{item.id}"


class BlogFeed(Feed):
    title = "Instanssi.org Blogi"
    link = "http://instanssi.org"
    description = "Instanssi-demopartyn uusimmat uutiset."

    def items(self, obj):
        entries = []
        for entry in BlogEntry.objects.filter(event=obj, public=True).order_by("-date")[:25]:
            entry.event_url = obj.mainurl
            entries.append(entry)
        return entries

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text

    def item_link(self, item) -> str:
        return f"{item.event_url}#{item.id}"
