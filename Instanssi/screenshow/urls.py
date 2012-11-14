# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.screenshow.views',
    url(r'^$', 'index', name="index"),
	url(r'^api/', 'api', name="api"),
)
