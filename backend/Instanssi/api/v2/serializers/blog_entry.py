from django.contrib.auth.models import User
from rest_framework.fields import CurrentUserDefault, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from Instanssi.ext_blog.models import BlogEntry


class BlogEntrySerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=User.objects.all(), default=CurrentUserDefault())
    created_by = SerializerMethodField()

    def get_created_by(self, entry: BlogEntry) -> str:
        return entry.user.get_username()

    class Meta:
        model = BlogEntry
        fields = ("id", "user", "date", "title", "text", "public", "event", "created_by")
        read_only_fields = ("id", "user", "date", "created_by")
