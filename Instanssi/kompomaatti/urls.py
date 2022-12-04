from django.conf.urls import url

from Instanssi.kompomaatti.views import (
    competition_details,
    competition_signout,
    competitions,
    compo_details,
    compo_vote,
    compoentry_delete,
    compoentry_edit,
    compos,
    entry_details,
    eventselect,
    index,
    validate_votecode_api,
    votecode,
)

app_name = "kompomaatti"


urlpatterns = [
    url(r"^$", eventselect, name="eventselect"),
    url(r"^(?P<event_id>\d+)/$", index, name="index"),
    url(r"^(?P<event_id>\d+)/compos/$", compos, name="compos"),
    url(
        r"^(?P<event_id>\d+)/compo/(?P<compo_id>\d+)/entry/(?P<entry_id>\d+)/edit/$",
        compoentry_edit,
        name="entry-edit",
    ),
    url(
        r"^(?P<event_id>\d+)/compo/(?P<compo_id>\d+)/entry/(?P<entry_id>\d+)/delete/$",
        compoentry_delete,
        name="entry-delete",
    ),
    url(
        r"^(?P<event_id>\d+)/compo/(?P<compo_id>\d+)/entry/(?P<entry_id>\d+)/$",
        entry_details,
        name="entry",
    ),
    url(r"^(?P<event_id>\d+)/compo/(?P<compo_id>\d+)/vote/$", compo_vote, name="compo-vote"),
    url(r"^(?P<event_id>\d+)/compo/(?P<compo_id>\d+)/$", compo_details, name="compo"),
    url(r"^(?P<event_id>\d+)/competitions/$", competitions, name="competitions"),
    url(
        r"^(?P<event_id>\d+)/competition/(?P<competition_id>\d+)/signout/$",
        competition_signout,
        name="competition-signout",
    ),
    url(
        r"^(?P<event_id>\d+)/competition/(?P<competition_id>\d+)/$",
        competition_details,
        name="competition",
    ),
    url(r"^(?P<event_id>\d+)/votecode/$", votecode, name="votecode"),
    url(
        r"^(?P<event_id>\d+)/validate_votecode_api/(?P<vote_code>[0-9a-z]+)/$",
        validate_votecode_api,
        name="validate_votecode_api",
    ),
]
