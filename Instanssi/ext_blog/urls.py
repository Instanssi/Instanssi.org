# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url, include
from Instanssi.ext_blog.views import BlogEntryFeed

urlpatterns = patterns(
    '',
    (r'^(?P<event_id>\d+)/rss/$', BlogEntryFeed()),
)
