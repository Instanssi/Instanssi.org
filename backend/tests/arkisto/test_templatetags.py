import pytest
from django.template import Context, Template

from Instanssi.arkisto.templatetags.arkisto_base_tags import dotfill, media_type

# ===== media_type filter =====


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("demo.mp4", "video"),
        ("clip.mkv", "video"),
        ("movie.webm", "video"),
        ("demo.avi", "video"),
        ("track.mp3", "audio"),
        ("song.ogg", "audio"),
        ("music.opus", "audio"),
        ("sound.flac", "audio"),
        ("readme.txt", "other"),
        ("archive.zip", "other"),
        ("image.png", "other"),
    ],
)
def test_media_type_extensions(filename, expected):
    assert media_type(filename) == expected


def test_media_type_none():
    assert media_type(None) == "other"


def test_media_type_empty_string():
    assert media_type("") == "other"


def test_media_type_case_insensitive():
    assert media_type("DEMO.MP4") == "video"
    assert media_type("Track.MP3") == "audio"


# ===== dotfill filter =====


def test_dotfill_basic():
    result = dotfill("Hello", 20)
    assert result.startswith("Hello ")
    assert result.endswith(".")
    assert len(result) == 20


def test_dotfill_exact_width():
    result = dotfill("x" * 18, 20)
    assert result == "x" * 18


def test_dotfill_exceeds_width():
    result = dotfill("x" * 25, 20)
    assert result == "x" * 25


def test_dotfill_short_string():
    result = dotfill("Hi", 10)
    assert result == "Hi ......."
    assert len(result) == 10


# ===== render_arkisto_nav tag =====


@pytest.mark.django_db
def test_render_arkisto_nav_returns_archived_events(archived_event):
    template = Template("{% load arkisto_base_tags %}{% render_arkisto_nav %}")
    rendered = template.render(Context({}))
    assert archived_event.tag in rendered


@pytest.mark.django_db
def test_render_arkisto_nav_excludes_non_archived(non_archived_event):
    template = Template("{% load arkisto_base_tags %}{% render_arkisto_nav %}")
    rendered = template.render(Context({}))
    assert non_archived_event.tag not in rendered


@pytest.mark.django_db
def test_render_arkisto_nav_empty_when_no_events():
    template = Template("{% load arkisto_base_tags %}{% render_arkisto_nav %}")
    rendered = template.render(Context({}))
    assert "event-tab" not in rendered
