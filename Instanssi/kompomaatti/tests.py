from django.test import TestCase
from Instanssi.kompomaatti.models import Entry


VALID_YOUTUBE_URLS = [
    # must handle various protocols in the video URL
    "http://www.youtube.com/v/asdf123456",
    "https://www.youtube.com/v/asdf123456/",
    "//www.youtube.com/v/asdf123456",
    "www.youtube.com/v/asdf123456",
    # must handle various other ways to define the video
    "www.youtube.com/watch?v=asdf123456",
    "http://youtu.be/asdf123456",
    "http://youtu.be/asdf123456/"
]


class KompomaattiTests(TestCase):
    def setUp(self):
        pass

    def test_youtube_urls(self):
        """Test that various YouTube URLs are parsed properly."""
        for url in VALID_YOUTUBE_URLS:
            print("Test URL: %s" % url)
            self.assertEqual(Entry.youtube_url_to_id(url), "asdf123456")
