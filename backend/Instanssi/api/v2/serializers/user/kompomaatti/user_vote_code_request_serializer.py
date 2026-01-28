from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import VoteCodeRequest


class UserVoteCodeRequestSerializer(ModelSerializer[VoteCodeRequest]):
    """Serializer for user's own vote code requests.

    Users can create and read their own vote code requests.
    The status field is read-only for users (only staff can change it).
    Event and user are set by the viewset, not from the request body.

    Status values:
    - 0: Pending
    - 1: Accepted (voting right granted)
    - 2: Rejected (no voting right)
    """

    class Meta:
        model = VoteCodeRequest
        fields = ("id", "event", "text", "status")
        extra_kwargs = {
            "id": {"read_only": True},
            "event": {"read_only": True},
            "text": {"required": True},
            "status": {"read_only": True},
        }
