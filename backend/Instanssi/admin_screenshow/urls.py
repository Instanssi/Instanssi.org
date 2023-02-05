from django.urls import path

from Instanssi.admin_screenshow.views import (
    config,
    index,
    irc_messages,
    ircmessage_delete,
    ircmessage_edit,
    message_delete,
    message_edit,
    messages,
    playlist,
    playlist_delete,
    playlist_edit,
    sponsor_delete,
    sponsor_edit,
    sponsors,
)

app_name = "admin_screenshow"


urlpatterns = [
    path("", index, name="index"),
    path("config/", config, name="config"),
    path("ircmessages/<int:message_id>/delete/", ircmessage_delete, name="delete-ircmessage"),
    path("ircmessages/<int:message_id>/edit/", ircmessage_edit, name="edit-ircmessage"),
    path("ircmessages/", irc_messages, name="ircmessages"),
    path("messages/<int:message_id>/delete/", message_delete, name="delete-message"),
    path("messages/<int:message_id>/edit/", message_edit, name="edit-message"),
    path("messages/", messages, name="messages"),
    path("sponsors/<int:sponsor_id>/delete/", sponsor_delete, name="delete-sponsor"),
    path("sponsors/<int:sponsor_id>/edit/", sponsor_edit, name="edit-sponsor"),
    path("sponsors/", sponsors, name="sponsors"),
    path("playlist/<int:video_id>/delete/", playlist_delete, name="delete-playlist"),
    path("playlist/<int:video_id>/edit/", playlist_edit, name="edit-playlist"),
    path("playlist/", playlist, name="playlist"),
]
