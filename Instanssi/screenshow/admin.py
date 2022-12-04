from django.contrib import admin

from Instanssi.screenshow.models import (
    IRCMessage,
    Message,
    NPSong,
    PlaylistVideo,
    ScreenConfig,
    Sponsor,
)

admin.site.register(IRCMessage)
admin.site.register(Message)
admin.site.register(Sponsor)
admin.site.register(PlaylistVideo)
admin.site.register(ScreenConfig)
admin.site.register(NPSong)
