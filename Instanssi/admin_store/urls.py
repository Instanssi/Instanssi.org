# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_store.views',
    url(r'^$', 'status', name="index"),
    url(r'^items/', 'items', name="items"),
    url(r'^status/', 'status', name="status"),
)