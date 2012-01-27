# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'kompomaatti.views',
    url(r'^$', 'index'),
    url(r'^compo/(?P<compo_id>\d+)/', 'compo'),
    url(r'^entry/(?P<entry_id>\d+)/', 'entry'),
    url(r'^compolist/', 'compolist'),
    url(r'^myentries/del/(?P<entry_id>\d+)/', 'delentry'),
    url(r'^myentries/edit/(?P<entry_id>\d+)/', 'editentry'),
    url(r'^myentries/add/(?P<compo_id>\d+)/', 'addentry'),
    url(r'^myentries/', 'myentries'),
    url(r'^admin/', 'admin'),
    url(r'^help/', 'help'),
    url(r'^logout/', 'dologout'),
)