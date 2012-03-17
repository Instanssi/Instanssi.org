# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'admin_blog.views',
    url(r'^$', 'index'),
    url(r'^write/', 'write'),
    url(r'^delete/(?P<entry_id>\d+)/', 'delete'),
    url(r'^edit/(?P<entry_id>\d+)/', 'edit'),
)
