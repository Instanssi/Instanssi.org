# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from Instanssi.ext_blog.views import blog_feed, blog_feed_all

urlpatterns = patterns(
    'Instanssi.ext_blog.views',
    url(r'^(?P<event_id>\d+)/rss/$', blog_feed(), name="rss"),
    url(r'^rss/$', blog_feed_all(), name="rss"),
)
