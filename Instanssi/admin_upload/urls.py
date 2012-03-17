# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'admin_upload.views',
    url(r'^$', 'index'),
    url(r'^upload/', 'upload'),
)