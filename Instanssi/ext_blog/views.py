from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from django.contrib.syndication.views import Feed

from Instanssi.ext_blog.models import BlogEntry


@dataclass
class RSSEntry:
    id: int
    title: str
    date: datetime
    text: str
    event_url: str


class BlogFeed(Feed):
    title = "Instanssi.org Blogi"
    link = "https://instanssi.org"
    description = "Instanssi-demopartyn uusimmat uutiset."

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

    def items(self) -> List[RSSEntry]:
        return [self.item_to_rss(entry) for entry in BlogEntry.get_latest()[:25]]
