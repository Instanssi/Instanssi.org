from django.urls import path

from Instanssi.arkisto.views import (
    entries_m3u8,
    entry_index,
    event_index,
    index,
    json_event,
    text_event,
    video_index,
)

app_name = "arkisto"


urlpatterns = [
    path("", index, name="index"),
    path("entry/<int:entry_id>/", entry_index, name="entry"),
    path("text_event/<int:event_id>/", text_event, name="text_event"),
    path("json_event/<int:event_id>/", json_event, name="json_event"),
    path("m3u8/<int:event_id>/", entries_m3u8, name="entries_m3u8"),
    path("event/<int:event_id>/", event_index, name="event"),
    path("video/<int:video_id>/", video_index, name="video"),
]
