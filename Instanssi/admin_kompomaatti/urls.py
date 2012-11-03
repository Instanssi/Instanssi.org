# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_kompomaatti.views',
    url(r'^$', 'index', name="admin-kompomaatti"),
    
    url(r'^compos/', 'compo_browse', name="admin-compos"),
    url(r'^editcompo/(?P<compo_id>\d+)/', 'compo_edit', name="admin-compo-edit"),
    url(r'^deletecompo/(?P<compo_id>\d+)/', 'compo_delete', name="admin-compo-delete"),
    
    url(r'^entries/', 'entry_browse', name="admin-entries"),
    url(r'^editentry/(?P<entry_id>\d+)/', 'entry_edit', name="admin-entry-edit"),
    url(r'^deleteentry/(?P<entry_id>\d+)/', 'entry_delete', name="admin-entry-delete"),
    
    url(r'^competitions/', 'competitions_browse', name="admin-competitions"),
    url(r'^editcompetition/(?P<competition_id>\d+)/', 'competition_edit', name="admin-competition-edit"),
    url(r'^deletecompetition/(?P<competition_id>\d+)/', 'competition_delete', name="admin-competition-delete"),
    url(r'^score/(?P<competition_id>\d+)/', 'competition_score', name="admin-score"),
    url(r'^participations/(?P<competition_id>\d+)/', 'competition_participations', name="admin-participations"),
    url(r'^participations_edit/(?P<competition_id>\d+)/edit/(?P<pid>\d+)/', 'competition_participation_edit', name="admin-participation-edit"),
    
    url(r'^results/', 'results', name="admin-results"),
    url(r'^votecodes/', 'votecodes', name="admin-votecodes"),
    url(r'^printcodes/', 'votecodes_print', name="admin-votecodes-print"),
    url(r'^votecoderequests/', 'votecoderequests', name="admin-votecoderequests"),
    url(r'^acceptreq/(?P<vcrid>\d+)/', 'votecoderequests_accept', name="admin-votecoderequest-accept"),
)