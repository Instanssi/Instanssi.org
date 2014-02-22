# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.kompomaatti.views',
    url(r'^$', 'eventselect', name="eventselect"),
    url(r'^api/$', 'api', name="api"),
    url(r'^(?P<event_id>\d+)/$', 'index', name="index"),
    url(r'^(?P<event_id>\d+)/compos/$', 'compos', name="compos"),
    url(r'^(?P<event_id>\d+)/compo/(?P<compo_id>\d+)/entry/(?P<entry_id>\d+)/edit/$', 'compoentry_edit', name="entry-edit"),
    url(r'^(?P<event_id>\d+)/compo/(?P<compo_id>\d+)/entry/(?P<entry_id>\d+)/delete/$', 'compoentry_delete', name="entry-delete"),
    url(r'^(?P<event_id>\d+)/compo/(?P<compo_id>\d+)/entry/(?P<entry_id>\d+)/$', 'entry_details', name="entry"),
    url(r'^(?P<event_id>\d+)/compo/(?P<compo_id>\d+)/vote/$', 'compo_vote', name="compo-vote"),
    url(r'^(?P<event_id>\d+)/compo/(?P<compo_id>\d+)/$', 'compo_details', name="compo"),
    url(r'^(?P<event_id>\d+)/competitions/$', 'competitions', name="competitions"),
    url(r'^(?P<event_id>\d+)/competition/(?P<competition_id>\d+)/signout/$', 'competition_signout', name="competition-signout"),
    url(r'^(?P<event_id>\d+)/competition/(?P<competition_id>\d+)/$', 'competition_details', name="competition"),
    url(r'^(?P<event_id>\d+)/votecode/$', 'votecode', name="votecode"),
)
