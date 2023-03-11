from django.contrib import admin
from imagekit.admin import AdminThumbnail

from Instanssi.kompomaatti.models import (
    AlternateEntryFile,
    Competition,
    CompetitionParticipation,
    Compo,
    Entry,
    EntryCollection,
    Event,
    Profile,
    TicketVoteCode,
    Vote,
    VoteCodeRequest,
    VoteGroup,
)


class TicketVoteCodeAdmin(admin.ModelAdmin):
    list_display = [
        "associated_to",
        "event",
        "ticket",
        "time",
    ]


class VoteCodeRequestAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "event",
        "status",
        "text",
    ]


class EntryAdmin(admin.ModelAdmin):
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


class EntryCollectionAdmin(admin.ModelAdmin):
    list_display = [
        "compo",
        "file",
        "updated_at",
    ]


class AlternateEntryFileAdmin(admin.ModelAdmin):
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
admin.site.register(EntryCollection, EntryCollectionAdmin)
admin.site.register(Profile)
admin.site.register(Competition)
admin.site.register(CompetitionParticipation)
admin.site.register(AlternateEntryFile, AlternateEntryFileAdmin)
