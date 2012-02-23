# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'arkisto.views',
    url(r'^$', 'index'),
    url(r'^entry/(?P<entry_id>\d+)/', 'entry'),
)