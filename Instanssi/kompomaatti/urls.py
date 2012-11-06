# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.kompomaatti.views',
    url(r'^$', 'index', name="index"),
    url(r'^compos/', 'compos', name="compos"),
    url(r'^compo/(?P<compo_id>\d+)/entry/(?P<entry_id>\d+)/edit/', 'compoentry_edit', name="entry-edit"),
    url(r'^compo/(?P<compo_id>\d+)/entry/(?P<entry_id>\d+)/delete/', 'compoentry_delete', name="entry-delete"),
    url(r'^compo/(?P<compo_id>\d+)/entry/(?P<entry_id>\d+)/', 'entry_details', name="entry"),
    url(r'^compo/(?P<compo_id>\d+)/vote/', 'compo_vote', name="compo-vote"),
    url(r'^compo/(?P<compo_id>\d+)/', 'compo_details', name="compo"),
    url(r'^competitions/', 'competitions', name="competitions"),
    url(r'^competition/(?P<competition_id>\d+)/signout/', 'competition_signout', name="competition-signout"),
    url(r'^competition/(?P<competition_id>\d+)/', 'competition_details', name="competition"),
    url(r'^profile/', 'profile', name="profile"),
    url(r'^logout/', 'do_logout', name="logout"),
    url(r'^login/', 'do_login', name="login"),
)
