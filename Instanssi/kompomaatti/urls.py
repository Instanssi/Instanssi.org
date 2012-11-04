# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.kompomaatti.views',
    url(r'^$', 'index', name="kompomaatti-index"),
    url(r'^compos/', 'compos', name="kompomaatti-compos"),
    url(r'^compo/(?P<compo_id>\d+)/', 'compo_details', name="kompomaatti-compo"),
    url(r'^compo/(?P<compo_id>\d+)/edit/(?P<entry_id>\d+)/', 'compoentry_edit', name="kompomaatti-entry-edit"),
    url(r'^compo/(?P<compo_id>\d+)/delete/(?P<entry_id>\d+)/', 'compoentry_delete', name="kompomaatti-entry-delete"),
    url(r'^competitions/', 'competitions', name="kompomaatti-competitions"),
    url(r'^competition/(?P<competition_id>\d+)/', 'competition_details', name="kompomaatti-competition"),
    url(r'^competition/(?P<competition_id>\d+)/signup_toggle/', 'competition_signup_toggle', name="kompomaatti-competition-sign"),
    url(r'^profile/', 'profile', name="kompomaatti-profile"),
    url(r'^login/', 'login', name="kompomaatti-login"),
    url(r'^logout/', 'do_logout', name="kompomaatti-logout"),
)
