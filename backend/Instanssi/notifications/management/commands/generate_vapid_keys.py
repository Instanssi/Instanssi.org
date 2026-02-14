import base64
from typing import Any

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from django.core.management.base import BaseCommand
from py_vapid import Vapid


class Command(BaseCommand):
    help = "Generate a VAPID key pair for Web Push notifications"

    def handle(self, *args: Any, **options: Any) -> None:
        v = Vapid()
        v.generate_keys()

        raw_private = v.private_key.private_numbers().private_value.to_bytes(32, "big")
        b64_private = base64.urlsafe_b64encode(raw_private).rstrip(b"=").decode()

        raw_public = v.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
        b64_public = base64.urlsafe_b64encode(raw_public).rstrip(b"=").decode()

        self.stdout.write(f'VAPID_PUBLIC_KEY = "{b64_public}"')
        self.stdout.write(f'VAPID_PRIVATE_KEY = "{b64_private}"')
