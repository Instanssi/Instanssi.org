# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.json_api.kompomaatti.views',
    url(r'^competitions/$', 'competitions', name="competitions_get"),
    url(r'^compos/$', 'compos_get', name="compos_get"),
    url(r'^events/', 'events_get', name="events_get"),
)
