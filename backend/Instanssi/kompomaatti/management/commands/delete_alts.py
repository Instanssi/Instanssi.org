import sys
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from Instanssi.kompomaatti.models import AlternateEntryFile


class Command(BaseCommand):
    help = "delete all alternate audio files (database entries and files on disk)"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-i",
            "--event",
            required=False,
            help="Only delete alternates for entries in this event",
            type=int,
        )

    def handle(self, *args: Any, **options: Any) -> None:
        qs = AlternateEntryFile.objects.get_queryset()
        if event_id := options.get("event"):
            sys.stderr.write(f"Deleting alternates for entries in event {event_id}\n")
            qs = qs.filter(entry__compo__event_id=int(event_id))

        count = 0
        for alt in qs.iterator():
            if alt.file:
                alt.file.delete(save=False)
            alt.delete()
            count += 1

        sys.stderr.write(f"Deleted {count} alternate file(s)\n")
