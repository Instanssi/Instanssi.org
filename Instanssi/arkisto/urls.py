# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.arkisto.views',
    url(r'^$', 'index'),
    url(r'^entry/(?P<entry_id>\d+)/', 'entry'),
    url(r'^event/(?P<event_id>\d+)/', 'event'),
    url(r'^video/(?P<video_id>\d+)/', 'video'),
)