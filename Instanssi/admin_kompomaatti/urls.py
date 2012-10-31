# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_kompomaatti.views',
    url(r'^$', 'compo_browse'),
    url(r'^compos/', 'compo_browse'),
    url(r'^editcompo/(?P<compo_id>\d+)/', 'compo_edit'),
    url(r'^deletecompo/(?P<compo_id>\d+)/', 'compo_delete'),
    url(r'^entries/', 'entry_browse'),
    url(r'^editentry/(?P<entry_id>\d+)/', 'entry_edit'),
    url(r'^deleteentry/(?P<entry_id>\d+)/', 'entry_delete'),
    url(r'^competitions/', 'competitions_browse'),
    url(r'^editcompetition/(?P<competition_id>\d+)/', 'competition_edit'),
    url(r'^deletecompetition/(?P<competition_id>\d+)/', 'competition_delete'),
    url(r'^results/', 'results'),
    url(r'^votecodes/', 'votecodes'),
    url(r'^printcodes/', 'votecodes_print'),
    url(r'^votecoderequests/', 'votecoderequests'),
    url(r'acceptreq/(?P<vcrid>\d+)/', 'votecoderequests_accept'),
)