# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_blog.views',
    url(r'^$', 'index', name="blog"),
    url(r'^delete/(?P<entry_id>\d+)/', 'delete', name="blog-delete"),
    url(r'^edit/(?P<entry_id>\d+)/', 'edit', name="blog-edit"),
)
