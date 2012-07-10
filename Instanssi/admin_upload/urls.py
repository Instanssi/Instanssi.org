# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_upload.views',
    url(r'^$', 'index'),
    url(r'^upload/', 'upload'),
    url(r'^delete/(?P<file_id>\d+)/', 'deletefile'),
)