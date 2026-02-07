import logging

from rest_framework.serializers import ModelSerializer

from Instanssi.users.models import User

logger = logging.getLogger(__name__)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")
