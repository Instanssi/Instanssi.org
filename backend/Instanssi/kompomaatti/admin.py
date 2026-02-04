from typing import TYPE_CHECKING

from django.contrib import admin
from imagekit.admin import AdminThumbnail

from Instanssi.kompomaatti.models import (
    AlternateEntryFile,
    Competition,
    CompetitionParticipation,
    Compo,
    Entry,
    Event,
    Profile,
    TicketVoteCode,
    Vote,
    VoteCodeRequest,
    VoteGroup,
)

if TYPE_CHECKING:
    _TicketVoteCodeAdminBase = admin.ModelAdmin[TicketVoteCode]
    _VoteCodeRequestAdminBase = admin.ModelAdmin[VoteCodeRequest]
    _EntryAdminBase = admin.ModelAdmin[Entry]
    _AlternateEntryFileAdminBase = admin.ModelAdmin[AlternateEntryFile]
else:
    _TicketVoteCodeAdminBase = admin.ModelAdmin
    _VoteCodeRequestAdminBase = admin.ModelAdmin
    _EntryAdminBase = admin.ModelAdmin
    _AlternateEntryFileAdminBase = admin.ModelAdmin


class TicketVoteCodeAdmin(_TicketVoteCodeAdminBase):
    list_display = [
        "associated_to",
        "event",
        "ticket",
        "time",
    ]


class VoteCodeRequestAdmin(_VoteCodeRequestAdminBase):
    list_display = [
        "user",
        "event",
        "status",
        "text",
    ]


class EntryAdmin(_EntryAdminBase):
    list_display = [
        "created_at",
        "name",
        "compo",
        "user",
        "creator",
        "entryfile",
        "disqualified",
        "admin_thumbnail",
    ]
    admin_thumbnail = AdminThumbnail(image_field="imagefile_thumbnail")


class AlternateEntryFileAdmin(_AlternateEntryFileAdminBase):
    list_display = [
        "entry",
        "codec",
        "container",
        "created_at",
        "updated_at",
        "file",
    ]


admin.site.register(Compo)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Event)
admin.site.register(Vote)
admin.site.register(VoteGroup)
admin.site.register(TicketVoteCode, TicketVoteCodeAdmin)
admin.site.register(VoteCodeRequest, VoteCodeRequestAdmin)
admin.site.register(Profile)
admin.site.register(Competition)
admin.site.register(CompetitionParticipation)
admin.site.register(AlternateEntryFile, AlternateEntryFileAdmin)
