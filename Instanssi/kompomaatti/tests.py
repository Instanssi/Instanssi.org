from django.test import TestCase
from Instanssi.kompomaatti.models import Entry


VALID_YOUTUBE_URLS = [
    # must handle various protocols and hostnames in the video URL
    "http://www.youtube.com/v/asdf123456",
    "https://www.youtube.com/v/asdf123456/",
    "//www.youtube.com/v/asdf123456",
    "www.youtube.com/v/asdf123456",
    "youtube.com/v/asdf123456/",
    # must handle various other ways to define the video
    "www.youtube.com/watch?v=asdf123456",
    "http://youtu.be/asdf123456",
    "https://youtu.be/asdf123456/"
]


class KompomaattiTests(TestCase):
    def setUp(self):
        pass

    def test_youtube_urls(self):
        """Test YouTube video id extraction from URLs."""
        for url in VALID_YOUTUBE_URLS:
            self.assertEqual(Entry.youtube_url_to_id(url), "asdf123456",
                             msg="failing URL: %s" % url)
