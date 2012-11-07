# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.main2013.views',
    url(r'^$', 'pageloader', {'templatename': 'index'}),
)
