# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'entryarchivaltool.views',
    url(r'^$', 'index'),
)