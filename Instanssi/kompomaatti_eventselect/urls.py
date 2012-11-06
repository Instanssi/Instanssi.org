# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.kompomaatti_eventselect.views',
    url(r'^$', 'index', name="index"),
)
