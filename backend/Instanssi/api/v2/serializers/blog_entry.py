from django.contrib.auth.models import User
from rest_framework.fields import CurrentUserDefault
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from Instanssi.ext_blog.models import BlogEntry


class BlogEntrySerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=User.objects.all(), default=CurrentUserDefault())

    class Meta:
        model = BlogEntry
        fields = ("id", "user", "date", "title", "text", "public", "event")
        read_only_fields = ("id", "user", "date")
