# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.json_api.screen.views',
    url(r'^np/$', 'song_get', name="song_get"),
    url(r'^np/set/$', 'song_set', name="song_set"),
)
