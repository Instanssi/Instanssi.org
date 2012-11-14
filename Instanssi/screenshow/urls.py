# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.screenshow.views',
    url(r'^(?P<event_id>\d+)/$', 'index', name="index"),
	url(r'^(?P<event_id>\d+)/api/', 'api', name="api"),
)
