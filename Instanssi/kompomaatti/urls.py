# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'kompomaatti.views',
    url(r'^$', 'index'),
    url(r'^compo/', 'compo'),
    url(r'^entry/', 'entry'),
)