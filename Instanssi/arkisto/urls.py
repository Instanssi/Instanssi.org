# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.arkisto.views import index, entry, event, video

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^entry/(?P<entry_id>\d+)/', entry, name="entry"),
    url(r'^event/(?P<event_id>\d+)/', event, name="event"),
    url(r'^video/(?P<video_id>\d+)/', video, name="video"),
]
