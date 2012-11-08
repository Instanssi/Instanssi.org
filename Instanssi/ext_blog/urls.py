# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url, include
from Instanssi.ext_blog.views import blog_feed

urlpatterns = patterns(
    'Instanssi.ext_blog.views',
    url(r'^(?P<event_id>\d+)/rss/$', blog_feed(), name="rss"),
)
