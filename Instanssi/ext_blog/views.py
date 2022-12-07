from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from django.contrib.syndication.views import Feed

from Instanssi.ext_blog.models import BlogEntry
from Instanssi.kompomaatti.models import Event


@dataclass
class RSSEntry:
    id: int
    title: str
    date: datetime
    text: str
    event_url: str


class BlogFeedBase(Feed):
    @staticmethod
    def item_to_rss(entry: BlogEntry, url: Optional[str] = None) -> RSSEntry:
        return RSSEntry(
            id=entry.id,
            date=entry.date,
            event_url=url or entry.event.mainurl,
            title=entry.title,
            text=entry.text,
        )

    def item_title(self, item: RSSEntry) -> str:
        return item.title

    def item_pubdate(self, item: RSSEntry) -> datetime:
        return item.date

    def item_description(self, item: RSSEntry) -> str:
        return item.text

    def item_link(self, item: RSSEntry) -> str:
        return f"{item.event_url}#{item.id}"


class BlogFeedAll(BlogFeedBase):
    title = "Instanssi.org Blogi"
    link = "https://instanssi.org"
    description = "Instanssi-demopartyn uusimmat uutiset."

    def items(self) -> List[RSSEntry]:
        entries = BlogEntry.objects.filter(public=True).order_by("-date")[:25]
        return [self.item_to_rss(entry) for entry in entries]


class BlogFeed(BlogFeedBase):
    title = "Instanssi.org Blogi"
    link = "https://instanssi.org"
    description = "Instanssi-demopartyn uusimmat uutiset."

    def items(self, obj: Event) -> List[RSSEntry]:
        entries = BlogEntry.objects.filter(event=obj, public=True).order_by("-date")[:25]
        return [self.item_to_rss(entry, obj.mainurl) for entry in entries]
