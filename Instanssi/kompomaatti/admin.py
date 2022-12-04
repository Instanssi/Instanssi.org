from django.contrib import admin
from imagekit.admin import AdminThumbnail
from Instanssi.kompomaatti.models import Compo, Entry, Event, Vote, VoteCodeRequest, Profile, Competition, \
    CompetitionParticipation, TicketVoteCode, VoteGroup, EntryCollection


class TicketVoteCodeAdmin(admin.ModelAdmin):
    list_display = [
        'associated_to',
        'event',
        'ticket',
        'time',
    ]


class VoteCodeRequestAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'event',
        'status',
        'text',
    ]


class EntryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'compo',
        'user',
        'creator',
        'entryfile',
        'disqualified',
        'admin_thumbnail',
    ]
    admin_thumbnail = AdminThumbnail(image_field='imagefile_thumbnail')


class EntryCollectionAdmin(admin.ModelAdmin):
    list_display = [
        'compo',
        'file',
        'updated_at',
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
