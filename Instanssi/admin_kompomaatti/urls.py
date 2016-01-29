# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_kompomaatti.views import index, competition_delete, competition_edit,\
    competition_participation_edit, compo_browse, compo_delete, compo_edit, competition_participations,\
    competition_score, competitions_browse, results, votecoderequests, votecoderequests_accept, votecodes,\
    votecodes_print, entries_csv, entry_browse, entry_delete, entry_edit, ticket_votecodes

urlpatterns = [
    url(r'^$', index, name="index"),
    
    url(r'^compos/', compo_browse, name="compos"),
    url(r'^editcompo/(?P<compo_id>\d+)/', compo_edit, name="compo-edit"),
    url(r'^deletecompo/(?P<compo_id>\d+)/', compo_delete, name="compo-delete"),
    
    url(r'^entries_csv/', entries_csv, name="entries_csv"),

    url(r'^entries/', entry_browse, name="entries"),
    url(r'^editentry/(?P<entry_id>\d+)/', entry_edit, name="entry-edit"),
    url(r'^deleteentry/(?P<entry_id>\d+)/', entry_delete, name="entry-delete"),
    
    url(r'^competitions/', competitions_browse, name="competitions"),
    url(r'^editcompetition/(?P<competition_id>\d+)/', competition_edit, name="competition-edit"),
    url(r'^deletecompetition/(?P<competition_id>\d+)/', competition_delete, name="competition-delete"),
    url(r'^score/(?P<competition_id>\d+)/', competition_score, name="score"),
    url(r'^participations/(?P<competition_id>\d+)/', competition_participations, name="participations"),
    url(r'^participations_edit/(?P<competition_id>\d+)/edit/(?P<pid>\d+)/', competition_participation_edit, name="participation-edit"),
    
    url(r'^results/', results, name="results"),
    url(r'^votecodes/', votecodes, name="votecodes"),
    url(r'^ticket_votecodes/', ticket_votecodes, name="ticket_votecodes"),
    url(r'^printcodes/', votecodes_print, name="votecodes-print"),
    url(r'^votecoderequests/', votecoderequests, name="votecoderequests"),
    url(r'^acceptreq/(?P<vcrid>\d+)/', votecoderequests_accept, name="votecoderequest-accept"),
]
