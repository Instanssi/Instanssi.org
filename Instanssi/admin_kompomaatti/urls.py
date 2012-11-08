# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_kompomaatti.views',
    url(r'^$', 'index', name="kompomaatti"),
    
    url(r'^compos/', 'compo_browse', name="compos"),
    url(r'^editcompo/(?P<compo_id>\d+)/', 'compo_edit', name="compo-edit"),
    url(r'^deletecompo/(?P<compo_id>\d+)/', 'compo_delete', name="compo-delete"),
    
    url(r'^entries/', 'entry_browse', name="entries"),
    url(r'^editentry/(?P<entry_id>\d+)/', 'entry_edit', name="entry-edit"),
    url(r'^deleteentry/(?P<entry_id>\d+)/', 'entry_delete', name="entry-delete"),
    
    url(r'^competitions/', 'competitions_browse', name="competitions"),
    url(r'^editcompetition/(?P<competition_id>\d+)/', 'competition_edit', name="competition-edit"),
    url(r'^deletecompetition/(?P<competition_id>\d+)/', 'competition_delete', name="competition-delete"),
    url(r'^score/(?P<competition_id>\d+)/', 'competition_score', name="score"),
    url(r'^participations/(?P<competition_id>\d+)/', 'competition_participations', name="participations"),
    url(r'^participations_edit/(?P<competition_id>\d+)/edit/(?P<pid>\d+)/', 'competition_participation_edit', name="participation-edit"),
    
    url(r'^results/', 'results', name="results"),
    url(r'^votecodes/', 'votecodes', name="votecodes"),
    url(r'^printcodes/', 'votecodes_print', name="votecodes-print"),
    url(r'^votecoderequests/', 'votecoderequests', name="votecoderequests"),
    url(r'^acceptreq/(?P<vcrid>\d+)/', 'votecoderequests_accept', name="votecoderequest-accept"),
)