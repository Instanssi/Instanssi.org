# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'arkisto.views',
    url(r'^$', 'index')
)