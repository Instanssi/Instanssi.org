import os
from secrets import token_hex

from django.core.files.storage import FileSystemStorage
from unidecode import unidecode


class ASCIIFileSystemStorage(FileSystemStorage):
    @staticmethod
    def stitch(*args):
        return "".join([*args]).strip(".")

    def get_valid_name(self, name: str) -> str:
        """
        Generate a clean ASCII filename, and add some variance with a random hex string to prevent collisions.
        """
        clean = super(ASCIIFileSystemStorage, self).get_valid_name(unidecode(name))
        base, ext = os.path.splitext(clean)
        if base and ext:
            return self.stitch(base, "_", token_hex(4), ext)
        if not ext and base.startswith("."):
            return self.stitch(token_hex(4), base)
        if not ext:
            return self.stitch(base, token_hex(4))
        return token_hex(8)
