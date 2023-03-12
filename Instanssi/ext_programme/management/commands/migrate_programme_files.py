from argparse import ArgumentParser, BooleanOptionalAction

from django.core.management.base import BaseCommand

from Instanssi.common.file_handling import migrate_all_file_fields
from Instanssi.ext_programme.models import ProgrammeEvent, generate_icon_path


class Command(BaseCommand):
    help = "Moves old files to new locations"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--dry-run", action=BooleanOptionalAction)

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        generators = {
            "icon_original": generate_icon_path,
            "icon2_original": generate_icon_path,
        }
        print("Found these errors:")
        for error in migrate_all_file_fields(ProgrammeEvent.objects.all(), generators, dry_run):
            print(error)
