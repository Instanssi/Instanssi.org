# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'arkistoija.views',
    url(r'^$', 'index'),
    url(r'^index/', 'index'),
)