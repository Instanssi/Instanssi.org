import sys

from django.core.management.base import BaseCommand

from Instanssi.kompomaatti.models import Entry


class Command(BaseCommand):
    help = "regenerate entry alternate audio files"

    def add_arguments(self, parser):
        parser.add_argument(
            "-i", "--event", required=False, help="Only regenerate entries in this event", type=int
        )

    def handle(self, *args, **options):
        qs = Entry.objects.get_queryset()
        if event_id := options.get("event"):
            sys.stderr.write(f"Regenerating entries in event {event_id}\n")
            qs = qs.filter(compo__event_id=int(event_id))
        for entry in qs.iterator():
            sys.stderr.write(f"Generating alternate audio files for entry {entry}\n")
            entry.generate_alternates()
