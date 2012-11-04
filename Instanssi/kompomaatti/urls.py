# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.kompomaatti.views',
    url(r'^$', 'index', name="kompomaatti-index"),
    url(r'^compos/', 'compos', name="kompomaatti-compos"),
    url(r'^compos/(?P<compo_id>\d+)/', 'compo_details', name="kompomaatti-compo"),
    url(r'^competitions/', 'competitions', name="kompomaatti-competitions"),
    url(r'^competition/(?P<competition_id>\d+)/', 'competition_details', name="kompomaatti-competition"),
    url(r'^profile/', 'profile', name="kompomaatti-profile"),
    url(r'^login/', 'login', name="kompomaatti-login"),
    url(r'^logout/', 'do_logout', name="kompomaatti-logout"),
)

"""
urlpatterns = patterns(
    'Instanssi.kompomaatti.views',
    url(r'^$', 'index.index'),
    url(r'^compo/(?P<compo_id>\d+)/', 'compo.compo'),
    url(r'^entry/(?P<entry_id>\d+)/', 'entry.entry'),
    url(r'^compolist/', 'compolist.compolist'),
    url(r'^myentries/del/(?P<entry_id>\d+)/', 'dashboard.delentry'),
    url(r'^myentries/edit/(?P<entry_id>\d+)/', 'dashboard.editentry'),
    url(r'^myentries/add/(?P<compo_id>\d+)/', 'dashboard.addentry'),
    url(r'^myentries/editprofile/', 'dashboard.editprofile'),
    url(r'^myentries/', 'dashboard.dashboard'),
    url(r'^help/', 'help.help'),
    url(r'^logout/', 'auth.dologout'),
)
"""