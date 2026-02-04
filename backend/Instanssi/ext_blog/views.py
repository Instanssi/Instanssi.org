from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from django.contrib.syndication.views import Feed

from Instanssi.ext_blog.models import BlogEntry


@dataclass
class RSSEntry:
    id: int
    title: str
    date: datetime
    text: str
    event_url: str


if TYPE_CHECKING:
    _BlogFeedBase = Feed[RSSEntry, RSSEntry]
else:
    _BlogFeedBase = Feed


class BlogFeed(_BlogFeedBase):
    title = "Instanssi.org Blogi"
    link = "https://instanssi.org"
    description = "Instanssi-demopartyn uusimmat uutiset."

    @staticmethod
    def item_to_rss(entry: BlogEntry, url: str | None = None) -> RSSEntry:
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

    def items(self) -> list[RSSEntry]:
        return [self.item_to_rss(entry) for entry in BlogEntry.get_latest()[:25]]
