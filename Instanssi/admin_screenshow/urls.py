# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_screenshow.views import index, config, ircmessage_delete, ircmessage_edit, ircmessages, \
    messages, message_delete, message_edit, sponsor_delete, sponsor_edit, sponsors, playlist, playlist_delete, \
    playlist_edit

app_name = "admin_screenshow"


urlpatterns = [
    url(r'^$', index, name="index"),
    
    url(r'^config/$', config, name="config"),
    
    url(r'^ircmessages/(?P<message_id>\d+)/delete/', ircmessage_delete, name="delete-ircmessage"),
    url(r'^ircmessages/(?P<message_id>\d+)/edit/', ircmessage_edit, name="edit-ircmessage"),
    url(r'^ircmessages/$', ircmessages, name="ircmessages"),
    
    url(r'^messages/(?P<message_id>\d+)/delete/', message_delete, name="delete-message"),
    url(r'^messages/(?P<message_id>\d+)/edit/', message_edit, name="edit-message"),
    url(r'^messages/$', messages, name="messages"),
    
    url(r'^sponsors/(?P<sponsor_id>\d+)/delete/', sponsor_delete, name="delete-sponsor"),
    url(r'^sponsors/(?P<sponsor_id>\d+)/edit/', sponsor_edit, name="edit-sponsor"),
    url(r'^sponsors/$', sponsors, name="sponsors"),
    
    url(r'^playlist/(?P<video_id>\d+)/delete/', playlist_delete, name="delete-playlist"),
    url(r'^playlist/(?P<video_id>\d+)/edit/', playlist_edit, name="edit-playlist"),
    url(r'^playlist/$', playlist, name="playlist"),
]
