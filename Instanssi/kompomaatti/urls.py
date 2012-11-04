# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.kompomaatti.views',
    url(r'^$', 'index', name="kompomaatti-index"),
    url(r'^compos/', 'compos', name="kompomaatti-compos"),
    url(r'^compo/(?P<compo_id>\d+)/', 'compo_details', name="kompomaatti-compo"),
    url(r'^competitions/', 'competitions', name="kompomaatti-competitions"),
    url(r'^competition/(?P<competition_id>\d+)/', 'competition_details', name="kompomaatti-competition"),
    url(r'^profile/', 'profile', name="kompomaatti-profile"),
    url(r'^login/', 'login', name="kompomaatti-login"),
    url(r'^logout/', 'do_logout', name="kompomaatti-logout"),
)
