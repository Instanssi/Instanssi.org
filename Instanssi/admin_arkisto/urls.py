# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'admin_arkisto.views',
    url(r'^$', 'index'),
    url(r'^archiver/', 'archiver'),
    url(r'^addtool/', 'addtool'),
)
