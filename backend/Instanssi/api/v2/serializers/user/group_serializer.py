from django.contrib.auth.models import Group
from rest_framework.serializers import ModelSerializer


class GroupSerializer(ModelSerializer[Group]):
    class Meta:
        model = Group
        fields = ("name",)
