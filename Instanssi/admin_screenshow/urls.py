# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_screenshow.views',
    url(r'^$', 'index', name="index"),
    url(r'^ircmessages/', 'ircmessages', name="ircmessages"),
    url(r'^messages/(?P<message_id>\d+)/delete/', 'message_delete', name="delete-message"),
    url(r'^messages/(?P<message_id>\d+)/edit/', 'message_edit', name="edit-message"),
    url(r'^messages/', 'messages', name="messages"),
    url(r'^sponsors/(?P<sponsor_id>\d+)/delete/', 'sponsor_delete', name="delete-sponsor"),
    url(r'^sponsors/(?P<sponsor_id>\d+)/edit/', 'sponsor_edit', name="edit-sponsor"),
    url(r'^sponsors/', 'sponsors', name="sponsors"),
)
