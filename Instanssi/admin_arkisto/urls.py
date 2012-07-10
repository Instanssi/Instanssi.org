# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_arkisto.views',
    url(r'^$', 'index'),
    url(r'^archiver/', 'archiver'),
    url(r'^addtool/', 'addtool'),
)
