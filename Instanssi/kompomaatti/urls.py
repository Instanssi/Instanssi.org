from django.conf.urls import url

from Instanssi.kompomaatti.views import dummy_index

app_name = "kompomaatti"

"""
Note that we overlay the new SPA kompomaatti on top of the Instanssi main website. These urls do not lead to
anything in this main website, but the new SPA site will respond to these. Therefore keep them for
compatibility.
"""
urlpatterns = [
    url(r"^$", dummy_index, name="eventselect"),
    url(r"^(?P<event_id>\d+)/$", dummy_index, name="index"),
    url(r"^(?P<event_id>\d+)/compo/(?P<compo_id>\d+)/$", dummy_index, name="compo"),
    url(r"^(?P<event_id>\d+)/competition/(?P<competition_id>\d+)/$", dummy_index, name="competition"),
]
