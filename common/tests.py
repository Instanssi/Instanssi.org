from django.test import TestCase
from common.misc import parse_youtube_video_id


class YoutubeUrlTestCase(TestCase):
    def test_youtu_be(self):
        self.assertEqual(parse_youtube_video_id('http://youtu.be/w34tvwoier8'), 'w34tvwoier8')

    def test_long_form(self):
        self.assertEqual(parse_youtube_video_id('http://www.youtube.com/watch?v=dbh4re56u4&feature=feedu'),
                         'dbh4re56u4')
        self.assertEqual(parse_youtube_video_id('https://www.youtube.com/watch?v=br56urn6u'),
                         'br56urn6u')

    def test_embed_form(self):
        self.assertEqual(parse_youtube_video_id('http://www.youtube.com/embed/w4v6be547'), 'w4v6be547')

    def test_short_embed_form(self):
        self.assertEqual(parse_youtube_video_id('http://www.youtube.com/v/egv5yber5yre5?version=3&amp;hl=en_US'),
                         'egv5yber5yre5')
