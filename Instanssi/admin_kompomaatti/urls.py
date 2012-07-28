# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_kompomaatti.views',
    url(r'^$', 'compo_browse'),
    url(r'^compos/', 'compo_browse'),
    url(r'^addcompo/', 'compo_add'),
    url(r'^editcompo/(?P<compo_id>\d+)/', 'compo_edit'),
    url(r'^entries/', 'entry_browse'),
    url(r'^addentry/', 'entry_add'),
    url(r'^editentry/(?P<entry_id>\d+)/', 'entry_edit'),
    url(r'^results/', 'results'),
    url(r'^votecodes/', 'votecodes'),
    url(r'^printcodes/', 'votecodes_print'),
    url(r'^addvotecodes/', 'votecodes_generate'),
    url(r'^votecoderequests/', 'votecoderequests'),
    url(r'acceptreq/(?P<vcrid>\d+)/', 'votecoderequests_accept'),
)