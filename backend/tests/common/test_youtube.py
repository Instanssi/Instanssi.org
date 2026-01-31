import pytest

from Instanssi.common.youtube import (
    InvalidStartTimeError,
    InvalidVideoIdError,
    YoutubeURL,
)


def test_valid_video_id():
    """Test that valid 11-character video IDs are accepted."""
    url = YoutubeURL(video_id="dQw4w9WgXcQ")
    assert url.video_id == "dQw4w9WgXcQ"


def test_valid_video_id_with_special_chars():
    """Test that video IDs with - and _ are accepted."""
    url = YoutubeURL(video_id="abc-def_123")
    assert url.video_id == "abc-def_123"


@pytest.mark.parametrize(
    "invalid_id,description",
    [
        ("abc123", "too short (6 chars)"),
        ("abcdefghijklm", "too long (13 chars)"),
        ("abc@def#123", "invalid characters"),
        ("abc def 123", "contains spaces"),
        ("", "empty string"),
    ],
)
def test_invalid_video_id_format(invalid_id, description):
    """Test that invalid video IDs raise InvalidVideoIdError."""
    with pytest.raises(InvalidVideoIdError):
        YoutubeURL(video_id=invalid_id)


def test_video_id_must_be_string():
    """Test that non-string video IDs raise InvalidVideoIdError."""
    with pytest.raises(InvalidVideoIdError):
        YoutubeURL(video_id=12345678901)  # type: ignore[arg-type]


def test_valid_start_time():
    """Test that valid integer start times are accepted."""
    url = YoutubeURL(video_id="dQw4w9WgXcQ", start=30)
    assert url.start == 30


def test_start_time_none():
    """Test that None start time is accepted."""
    url = YoutubeURL(video_id="dQw4w9WgXcQ", start=None)
    assert url.start is None


def test_start_time_must_be_int():
    """Test that non-integer start times raise InvalidStartTimeError."""
    with pytest.raises(InvalidStartTimeError):
        YoutubeURL(video_id="dQw4w9WgXcQ", start="30")  # type: ignore[arg-type]


def test_start_time_float_rejected():
    """Test that float start times raise InvalidStartTimeError."""
    with pytest.raises(InvalidStartTimeError):
        YoutubeURL(video_id="dQw4w9WgXcQ", start=30.5)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "input_data,expected",
    [
        ("http://youtu.be/w34tvwoier8", "w34tvwoier8"),
        ("//youtu.be/w34tvwoier8", "w34tvwoier8"),
        ("http://www.youtube.com/watch?v=dbh4re56u4A&feature=feedu", "dbh4re56u4A"),
        ("https://www.youtube.com/watch?v=br56urn6uAB", "br56urn6uAB"),
        ("www.youtube.com/watch?v=br56urn6uAB", "br56urn6uAB"),
        ("youtube.com/watch?v=br56urn6uAB", "br56urn6uAB"),
        ("http://www.youtube.com/embed/w4v6be547AB", "w4v6be547AB"),
        ("http://www.youtube.com/v/egv5yber5yr?version=3&amp;hl=en_US", "egv5yber5yr"),
    ],
)
def test_youtube_from_url(input_data, expected):
    assert YoutubeURL.from_url(input_data).video_id == expected


@pytest.mark.parametrize(
    "input_url,expected_start",
    [
        # Plain integers
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30", 30),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&start=45", 45),
        # Seconds only
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s", 30),
        # Minutes and seconds
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1m30s", 90),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=2m", 120),
        # Hours, minutes, and seconds
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1h2m30s", 3750),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1h", 3600),
        # No start time
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", None),
    ],
)
def test_youtube_from_url_with_start(input_url, expected_start):
    """Test that start time is correctly parsed from URLs."""
    url = YoutubeURL.from_url(input_url)
    assert url.start == expected_start


def test_url_normalizes_t_to_start():
    """Test that URLs with 't' parameter are normalized to 'start' in output."""
    url = YoutubeURL.from_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=45")
    assert url.start == 45
    assert "start=45" in url.link_url
    assert "&t=" not in url.link_url


def test_link_url_uses_start_parameter():
    """Test that link_url always uses 'start' parameter for start time."""
    url = YoutubeURL(video_id="dQw4w9WgXcQ", start=30)
    assert url.link_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ&start=30"


def test_embed_url_uses_start_parameter():
    """Test that embed_url uses 'start' parameter."""
    url = YoutubeURL(video_id="dQw4w9WgXcQ", start=30)
    assert url.embed_url == "https://www.youtube.com/embed/dQw4w9WgXcQ?start=30"
