# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_blog.views',
    url(r'^$', 'index', name="admin-blog"),
    url(r'^delete/(?P<entry_id>\d+)/', 'delete', name="admin-blog-delete"),
    url(r'^edit/(?P<entry_id>\d+)/', 'edit', name="admin-blog-edit"),
)
