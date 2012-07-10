# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

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
    url(r'^admin/givecode/(?P<vcrid>\d+)/', 'admin.givecode'),
    url(r'^admin/results/(?P<compo_id>\d+)/', 'admin.results'),
    url(r'^admin/editcompo/(?P<compo_id>\d+)/', 'admin.editcompo'),
    url(r'^admin/editentry/(?P<entry_id>\d+)/', 'admin.editentry'),
    url(r'^admin/addcompo/', 'admin.addcompo'),
    url(r'^admin/printcodes/', 'admin.printcodes'),
    url(r'^admin/', 'admin.admin'),
    url(r'^help/', 'help.help'),
    url(r'^logout/', 'auth.dologout'),
)