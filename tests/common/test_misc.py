import pytest

from Instanssi.common.misc import parse_youtube_video_id


@pytest.mark.parametrize(
    "input_data,expected",
    [
        ("http://youtu.be/w34tvwoier8", "w34tvwoier8"),
        ("//youtu.be/w34tvwoier8", "w34tvwoier8"),
        ("http://www.youtube.com/watch?v=dbh4re56u4&feature=feedu", "dbh4re56u4"),
        ("https://www.youtube.com/watch?v=br56urn6u", "br56urn6u"),
        ("www.youtube.com/watch?v=br56urn6u", "br56urn6u"),
        ("youtube.com/watch?v=br56urn6u", "br56urn6u"),
        ("http://www.youtube.com/embed/w4v6be547", "w4v6be547"),
        ("http://www.youtube.com/v/egv5yber5yre5?version=3&amp;hl=en_US", "egv5yber5yre5"),
    ],
)
def test_parse_youtube_video_id(input_data, expected):
    assert parse_youtube_video_id(input_data) == expected
