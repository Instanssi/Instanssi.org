# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.arkisto.views',
    url(r'^$', 'index', name="index"),
    url(r'^entry/(?P<entry_id>\d+)/', 'entry', name="entry"),
    url(r'^event/(?P<event_id>\d+)/', 'event', name="event"),
    url(r'^video/(?P<video_id>\d+)/', 'video', name="video"),
)