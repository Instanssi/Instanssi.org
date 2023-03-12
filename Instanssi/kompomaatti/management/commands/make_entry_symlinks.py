import json
from argparse import ArgumentParser, FileType

from django.conf import settings
from django.core.management.base import BaseCommand

from Instanssi.kompomaatti.models import Entry


class Command(BaseCommand):
    help = "regenerate entry alternate audio files"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--input", type=FileType("rb"), required=True)
        parser.add_argument("--count", type=int, default=-1)

    def make_compat_symlink(self, entry: Entry, values: dict, name: str) -> None:
        if not values[name]:
            return
        field = getattr(entry, name)
        old_path = settings.MEDIA_ROOT / values[name]
        new_path = settings.MEDIA_ROOT / field.name
        old_path.parent.mkdir(exist_ok=True)
        print(old_path, new_path)
        old_path.symlink_to(new_path)

    def handle(self, *args, **options):
        data = json.loads(options["input"].read())
        c = 1
        for entry in Entry.objects.iterator():
            old_values = data[str(entry.id)]
            self.make_compat_symlink(entry, old_values, "entryfile")
            self.make_compat_symlink(entry, old_values, "sourcefile")
            self.make_compat_symlink(entry, old_values, "imagefile_original")
            if 0 < options["count"] <= c:
                break
            c += 1
