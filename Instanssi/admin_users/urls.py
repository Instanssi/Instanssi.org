# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_users.views import index, delete, edit, users, log, apps, delete_app

app_name = "admin_users"


urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^users/(?P<su_id>\d+)/delete/', delete, name="delete"),
    url(r'^users/(?P<su_id>\d+)/edit/', edit, name="edit"),
    url(r'^users/$', users, name="users"),
    url(r'^apps/(?P<app_id>\d+)/delete/', delete_app, name="delete_app"),
    url(r'^apps/$', apps, name="apps"),
    url(r'^log/$', log, name="log"),
]
