# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.json_api.views',
    url(r'^happenings/', 'happenings_api', name="happenings-api"),
    url(r'^events/(?P<hid>\d+)/', 'events_api', name="events-api"),
)
