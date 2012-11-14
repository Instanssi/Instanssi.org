# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.screenshow.views',
    url(r'^(?P<event_id>\d+)/$', 'index', name="index"),
	url(r'^(?P<event_id>\d+)/api/events/', 'events_api', name="events-api"),
    url(r'^(?P<event_id>\d+)/api/irc/', 'irc_api', name="irc-api"),
)
