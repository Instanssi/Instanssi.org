from typing import Callable

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models.fields.files import FieldFile

from Instanssi.kompomaatti.models import (
    Entry,
    generate_entry_file_path,
    generate_entry_image_path,
    generate_entry_source_path,
)


class FileError(Exception):
    pass


class Skip(Exception):
    pass


class Command(BaseCommand):
    help = "Moves old files to new locations"

    def migrate_file(self, entry: Entry, field: FieldFile, generator: Callable) -> str:
        new_dir = generator(entry, field.name)
        src_path = (settings.MEDIA_ROOT / field.name).resolve()
        dst_path = (settings.MEDIA_ROOT / new_dir).resolve()
        if not src_path.exists():
            raise FileError(f"Source file does not exist: {src_path}")
        if dst_path.exists():
            raise FileError(f"Destination file already exists: {dst_path}")
        print(f"Moving {src_path} to {dst_path}")
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.rename(dst_path)
        return new_dir

    def handle(self, *args, **options):
        generators = {
            "entryfile": generate_entry_file_path,
            "sourcefile": generate_entry_source_path,
            "imagefile_original": generate_entry_image_path,
        }

        errors = []
        skipped = 0
        for entry in Entry.objects.iterator():
            migrated = []
            for field_name, generator in generators.items():
                try:
                    field_file = getattr(entry, field_name)
                    if field_file:
                        field_file.name = self.migrate_file(entry, field_file, generator)
                        migrated.append(field_name)
                except FileError as err:
                    errors.append(str(err))
                except Skip:
                    skipped += 1
            entry.save(update_fields=migrated)

        print(f"Skipped {skipped} entries")
        print("Found these errors:")
        for error in errors:
            print(error)
