from django.urls import path

from Instanssi.kompomaatti.views import dummy_index

app_name = "kompomaatti"

"""
Note that we overlay the new SPA kompomaatti on top of the Instanssi main website. These urls do not lead to
anything in this main website, but the new SPA site will respond to these. Therefore keep them for
compatibility.
"""
urlpatterns = [
    path("", dummy_index, name="eventselect"),
    path("<int:event_id>/", dummy_index, name="index"),
    path("<int:event_id>/compo/<int:compo_id>/", dummy_index, name="compo"),
    path("<int:event_id>/competition/<int:competition_id>/", dummy_index, name="competition"),
]
