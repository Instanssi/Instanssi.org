import logging

from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

logger = logging.getLogger(__name__)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")
