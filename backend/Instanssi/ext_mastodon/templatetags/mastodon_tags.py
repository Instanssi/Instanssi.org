from __future__ import annotations

import logging
from datetime import datetime
from typing import Final, List, TypedDict

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


def filter_toots(toot: dict) -> bool:
    if toot.get("sensitive"):
        return False
    if toot.get("visibility") != "public":
        return False
    account = toot.get("account")
    if not account:
        return False
    if account.get("acct") != "instanssi":
        return False
    return True


def map_toots(obj: dict) -> Toot:
    return dict(
        username=obj["account"]["display_name"],
        user_url=obj["account"]["url"],
        url=obj["url"],
        content=mark_safe(nh3.clean(obj["content"], tags={"a", "p"})),
        created_at=obj["created_at"],
    )


def init_mastodon():
    return Mastodon(
        access_token=settings.MASTODON_ACCESS_TOKEN,
        api_base_url=settings.MASTODON_BASE_URL,
    )


def fetch_timeline(limit: int) -> List[dict]:
    if not settings.MASTODON_BASE_URL:
        return []
    try:
        return init_mastodon().timeline(limit=50)[:limit]
    except Exception as e:
        log.exception("Mastodon error: %s", e)
    return []


@register.inclusion_tag("ext_mastodon/timeline.html", name="mastodon_timeline")
def render_mastodon_timeline(limit: int = 10, timeout: int = 60 * 30) -> dict:
    timeline: List[Toot] = cache.get(MASTODON_CACHE_KEY)
    if not timeline:
        timeline = list(map(map_toots, filter(filter_toots, fetch_timeline(limit))))
        cache.set(MASTODON_CACHE_KEY, timeline, timeout)
    return dict(timeline=timeline)
