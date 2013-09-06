# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_upload.views',
    url(r'^$', 'index', name="index"),
    url(r'^delete/(?P<file_id>\d+)/', 'deletefile', name="delete"),
    url(r'^edit/(?P<file_id>\d+)/', 'editfile', name="edit"),
)