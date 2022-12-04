from django.contrib import admin
from Instanssi.screenshow.models import IRCMessage, Message, Sponsor, PlaylistVideo, ScreenConfig, NPSong


admin.site.register(IRCMessage)
admin.site.register(Message)
admin.site.register(Sponsor)
admin.site.register(PlaylistVideo)
admin.site.register(ScreenConfig)
admin.site.register(NPSong)
