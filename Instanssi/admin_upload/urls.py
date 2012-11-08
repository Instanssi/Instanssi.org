# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_upload.views',
    url(r'^$', 'index', name="uploads"),
    url(r'^delete/(?P<file_id>\d+)/', 'deletefile', name="upload-delete"),
    url(r'^edit/(?P<file_id>\d+)/', 'editfile', name="upload-edit"),
)