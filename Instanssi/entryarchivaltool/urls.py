# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.entryarchivaltool.views',
    url(r'^$', 'index'),
)