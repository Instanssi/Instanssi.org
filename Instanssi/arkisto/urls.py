# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.arkisto.views',
    url(r'^$', 'index', name="archive"),
    url(r'^entry/(?P<entry_id>\d+)/', 'entry', name="archive-entry"),
    url(r'^event/(?P<event_id>\d+)/', 'event', name="archive-event"),
    url(r'^video/(?P<video_id>\d+)/', 'video', name="archive-video"),
)