# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_users.views import index, delete, edit, users, log, tokens, add_token, invalidate_token

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^users/(?P<su_id>\d+)/delete/', delete, name="delete"),
    url(r'^users/(?P<su_id>\d+)/edit/', edit, name="edit"),
    url(r'^users/$', users, name="users"),
    url(r'^tokens/add/$', add_token, name="add_token"),
    url(r'^tokens/invalidate/$', invalidate_token, name="invalidate_token"),
    url(r'^tokens/$', tokens, name="tokens"),
    url(r'^log/$', log, name="log"),
]
