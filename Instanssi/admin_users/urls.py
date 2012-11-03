# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_users.views',
    url(r'^$', 'superusers'),
    url(r'^superusers/', 'superusers', name="admin-superusers"),
    url(r'^deletesu/(?P<su_id>\d+)/', 'deletesu', name="admin-deletesu"),
    url(r'^editsu/(?P<su_id>\d+)/', 'editsu', name="admin-editsu"),
    url(r'^openid/', 'openid', name="admin-openid"),
    url(r'^deleteopenid/(?P<user_id>\d+)/', 'deleteopenid', name="admin-deleteopenid"),
)