import logging
from datetime import datetime
from typing import Any, Final, TypedDict

import nh3
from django import template
from django.conf import settings
from django.core.cache import cache
from django.utils.safestring import mark_safe
from mastodon import Mastodon

log = logging.getLogger(__name__)

register = template.Library()

MASTODON_CACHE_KEY: Final[str] = "mastodon_timeline"


class Toot(TypedDict):
    """ref: https://mastodonpy.readthedocs.io/en/stable/02_return_values.html#toot-status-dicts"""

    username: str
    user_url: str
    url: str
    content: str
    created_at: datetime


def filter_toots(toot: dict[str, Any]) -> bool:
    if toot.get("sensitive"):
        return False
    if toot.get("visibility") != "public":
        return False
    return True


def map_toots(obj: dict[str, Any]) -> Toot:
    return dict(
        username=obj["account"]["display_name"],
        user_url=obj["account"]["url"],
        url=obj["url"],
        content=mark_safe(nh3.clean(obj["content"], tags={"a", "p", "br"})),
        created_at=obj["created_at"],
    )


def init_mastodon() -> Mastodon:
    return Mastodon(
        access_token=settings.MASTODON_ACCESS_TOKEN,
        api_base_url=settings.MASTODON_BASE_URL,
    )


def fetch_timeline(limit: int) -> list[dict[str, Any]]:
    if not settings.MASTODON_BASE_URL:
        return []
    try:
        mastodon = init_mastodon()
        account = mastodon.account_lookup(settings.MASTODON_ACCOUNT_NAME)
        return mastodon.account_statuses(
            account["id"], exclude_reblogs=True, exclude_replies=True, limit=25
        )[:limit]
    except Exception as e:
        log.exception("Mastodon error: %s", e)
    return []


@register.inclusion_tag("ext_mastodon/timeline.html", name="mastodon_timeline")
def render_mastodon_timeline(limit: int = 10, timeout: int = 60 * 30) -> dict[str, Any]:
    timeline: list[Toot] = cache.get(MASTODON_CACHE_KEY)
    if not timeline:
        timeline = list(map(map_toots, filter(filter_toots, fetch_timeline(limit))))
        cache.set(MASTODON_CACHE_KEY, timeline, timeout)
    return dict(timeline=timeline)
