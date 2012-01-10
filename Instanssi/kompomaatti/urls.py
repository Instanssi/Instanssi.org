# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'kompomaatti.views',
    url(r'^$', 'index'),
    url(r'^compo/(?P<compo_id>\d+)/', 'compo'),
    url(r'^entry/(?P<entry_id>\d+)/', 'entry'),
    url(r'^compolist/', 'compolist'),
    url(r'^myprods/', 'myprods'),
    url(r'^help/', 'help'),
)