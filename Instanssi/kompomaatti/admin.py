# -*- coding: utf-8 -*-

from django.contrib import admin
from Instanssi.kompomaatti.models import Compo, Entry, Event, Vote, VoteCode, VoteCodeRequest, Profile, Competition, \
    CompetitionParticipation, TicketVoteCode

admin.site.register(Compo)
admin.site.register(Entry)
admin.site.register(Event)
admin.site.register(Vote)
admin.site.register(TicketVoteCode)
admin.site.register(VoteCode)
admin.site.register(VoteCodeRequest)
admin.site.register(Profile)
admin.site.register(Competition)
admin.site.register(CompetitionParticipation)
