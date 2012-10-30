# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_arkisto.views',
    url(r'^$', 'archiver'),
    url(r'^archiver/', 'archiver'),
    url(r'^vids/', 'vids'),
    url(r'^vidcats/', 'cats'),
    url(r'^deletevid/(?P<video_id>\d+)/', 'deletevid'),
    url(r'^deletecat/(?P<category_id>\d+)/', 'deletecat'),
    url(r'^editvid/(?P<video_id>\d+)/', 'editvid'),
    url(r'^editcat/(?P<category_id>\d+)/', 'editcat'),
)
