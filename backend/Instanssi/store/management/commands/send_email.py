from django.core.management.base import BaseCommand

from Instanssi.store.models import Receipt


class Command(BaseCommand):
    help = "Send receipt email"

    def add_arguments(self, parser):
        parser.add_argument("-r", "--receipt", required=True, type=int)

    def handle(self, *args, **options):
        receipt = Receipt.objects.get(pk=options["receipt"])
        print(f"Sending receipt {receipt.id} to {receipt.mail_to}")
        receipt.send()
