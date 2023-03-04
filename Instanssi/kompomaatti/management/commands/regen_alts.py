from django.core.management.base import BaseCommand

from Instanssi.kompomaatti.models import Entry


class Command(BaseCommand):
    help = "regenerate entry alternate audio files"

    def handle(self, *args, **options):
        for entry in Entry.objects.iterator():
            entry.generate_alternates()
