import logging

from django.utils import timezone
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.screenshow.models import IRCMessage, Message, NPSong, Sponsor

logger = logging.getLogger(__name__)


class SongSerializer(ModelSerializer):
    class Meta:
        model = NPSong
        fields = ("id", "event", "title", "artist", "time", "state")
        extra_kwargs = {
            "state": {"read_only": True},
            "time": {"read_only": True},
            "id": {"read_only": True},
        }

    def create(self, validated_data: dict) -> NPSong:
        # Set old playing songs to stopped
        NPSong.objects.filter(event=validated_data["event"], state=0).update(state=1)

        # Add new song, set state to playing
        song = NPSong(**validated_data)
        song.state = 0
        song.time = timezone.now()
        song.save()
        return song


class SponsorSerializer(ModelSerializer):
    logo_url = SerializerMethodField()
    logo_scaled_url = SerializerMethodField()

    def get_logo_url(self, obj: Sponsor) -> str:
        return self.context["request"].build_absolute_uri(obj.logo.url)

    def get_logo_scaled_url(self, obj: Sponsor) -> str:
        return self.context["request"].build_absolute_uri(obj.logo_scaled.url)

    class Meta:
        model = Sponsor
        fields = ("id", "event", "name", "logo_url", "logo_scaled_url")
        extra_kwargs = {}


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "event", "show_start", "show_end", "text")
        extra_kwargs = {}


class IRCMessageSerializer(ModelSerializer):
    class Meta:
        model = IRCMessage
        fields = ("id", "event", "date", "nick", "message")
        extra_kwargs = {}
