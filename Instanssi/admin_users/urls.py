# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_users.views',
    url(r'^$', 'users'),
    url(r'^users/', 'users', name="admin-users"),
    url(r'^delete/(?P<su_id>\d+)/', 'delete', name="admin-users-delete"),
    url(r'^edit/(?P<su_id>\d+)/', 'edit', name="admin-users-edit"),
)