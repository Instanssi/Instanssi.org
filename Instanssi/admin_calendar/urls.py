# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'admin_calendar.views',
    url(r'^$', 'index'),
    url(r'^json/events/', 'api_events', {'event_name': 'events'}),
)
