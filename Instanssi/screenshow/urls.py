from django.urls import path

from Instanssi.screenshow.views import (
    events_api,
    index,
    irc_api,
    messages_api,
    playing_api,
    playlist_api,
    settings_api,
)

app_name = "screenshow"


urlpatterns = [
    path("<int:event_id>/", index, name="index"),
    path("<int:event_id>/api/events/", events_api, name="events-api"),
    path("<int:event_id>/api/irc/", irc_api, name="irc-api"),
    path("<int:event_id>/api/messages/", messages_api, name="messages-api"),
    path("<int:event_id>/api/playlist/", playlist_api, name="playlist-api"),
    path("<int:event_id>/api/settings/", settings_api, name="settings-api"),
    path("<int:event_id>/api/playing/", playing_api, name="playing-api"),
]
