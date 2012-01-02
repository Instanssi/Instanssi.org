# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'main2012.views',
    url(r'^$', 'index'),
)