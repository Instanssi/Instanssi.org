# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_blog.views',
    url(r'^$', 'index', name="index"),
    url(r'^delete/(?P<entry_id>\d+)/', 'delete', name="delete"),
    url(r'^edit/(?P<entry_id>\d+)/', 'edit', name="edit"),
)
