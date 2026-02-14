import os
from datetime import datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any

from auditlog.registry import auditlog
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q, QuerySet
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from Instanssi.common.file_handling import clean_filename, generate_upload_path
from Instanssi.common.html.fields import SanitizedHtmlField
from Instanssi.kompomaatti.models import Event
from Instanssi.store.utils.receipt import ReceiptParams


def generate_image_path(item: "StoreItem", filename: str) -> str:
    slug = clean_filename(Path(filename).stem)
    event = item.event
    if event is None:
        raise ValueError("StoreItem must have an event to generate image path")
    dt = datetime.combine(event.date, time(0, 0, 0, 0))
    return generate_upload_path(
        original_file=filename,
        path=settings.MEDIA_STORE_IMAGES,
        slug=slug,
        timestamp=dt,
    )


class StoreItem(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name="Tapahtuma",
        help_text="Tapahtuma johon tuote liittyy.",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    name = models.CharField("Tuotteen nimi", help_text="Tuotteen lyhyt nimi.", max_length=255)
    description = SanitizedHtmlField("Tuotteen kuvaus", help_text="Tuotteen pitkä kuvaus.")
    price = models.DecimalField(
        "Tuotteen hinta", help_text="Tuotteen hinta.", max_digits=5, decimal_places=2
    )
    max = models.IntegerField(
        "Kappaletta saatavilla",
        help_text="Kuinka monta kappaletta on ostettavissa ennen myynnin lopettamista.",
    )
    available = models.BooleanField(
        "Ostettavissa", default=False, help_text="Ilmoittaa, näkyykö tuote kaupassa."
    )
    imagefile_original = models.ImageField(
        "Tuotekuva",
        max_length=255,
        upload_to=generate_image_path,
        help_text="Edustava kuva tuotteelle.",
        blank=True,
        null=True,
    )
    imagefile_thumbnail = ImageSpecField([ResizeToFill(64, 64)], source="imagefile_original", format="PNG")
    max_per_order = models.IntegerField(
        "Maksimi per tilaus",
        default=10,
        help_text="Kuinka monta kappaletta voidaan ostaa kerralla.",
    )
    sort_index = models.IntegerField(
        "Järjestysarvo",
        default=0,
        help_text="Tuotteet esitetään kaupassa tämän luvun mukaan järjestettynä, pienempilukuiset ensin.",
    )
    discount_amount = models.IntegerField(
        "Alennusmäärä",
        default=-1,
        help_text="Pienin määrä tuotteita joka oikeuttaa alennukseen (-1 = ei mitään)",
    )
    discount_percentage = models.IntegerField(
        "Alennusprosentti",
        default=0,
        help_text="Alennuksen määrä prosentteina kun tuotteiden määrä saavuttaa alennusmäärän.",
    )
    is_ticket = models.BooleanField(
        "Tuote on lipputuote",
        default=False,
        help_text="Tuote on lipputuote, ja sitä voi käyttää esim. kompomaatissa äänestysoikeuden hankkimiseen",
    )
    is_secret = models.BooleanField(
        "Tuote on salainen",
        default=False,
        help_text="Tuote näkyy kaupassa vain salaisella linkillä",
    )
    secret_key = models.CharField(
        "Salasana",
        blank=True,
        max_length=255,
        help_text="Salaisen linkin avain. Jos salasana on kissa, salainen tuote näkyy vain osoitteessa https://instanssi.org/store/order/?secret_key=kissa",
    )

    def is_discount_available(self) -> bool:
        """Returns True if a discount exists for this item."""
        return self.discount_amount >= 0

    @property
    def variants(self) -> QuerySet["StoreItemVariant"]:
        """Returns a queryset with the available item variants"""
        return StoreItemVariant.objects.filter(item=self)

    def get_discount_factor(self) -> float:
        """Gets the potential discount factor, for views/templates/JS.

        Decimal arithmetic is used for actual price calculations."""
        return (100.0 - self.discount_percentage) / 100.0

    def is_discount_enabled(self, amount: int) -> bool:
        """Returns True if discount applies to a specific quantity of this."""
        return self.is_discount_available() and amount >= self.discount_amount

    def image_available(self) -> bool:
        full_path = os.path.join(settings.MEDIA_ROOT, self.imagefile_original.name)
        return os.path.isfile(full_path)

    def get_discounted_unit_price(self, amount: int) -> Decimal:
        """Returns decimal price of item considering any quantity discount."""
        if self.is_discount_enabled(amount):
            factor = (Decimal(100) - Decimal(self.discount_percentage)) / 100
            price = self.price * factor
        else:
            price = self.price
        # If we need to consider rounding direction, this might be the place.
        # Pass "rounding=METHOD" as second argument.
        return price.quantize(Decimal("0.01"))

    def get_discounted_subtotal(self, amount: int) -> Decimal:
        """Returns decimal subtotal for a specific number of items, considering
        any quantity discount."""
        return self.get_discounted_unit_price(amount) * amount

    def num_available(self) -> int:
        return min(self.max - self.num_sold(), self.max_per_order)

    def num_in_store(self) -> int:
        return self.max - self.num_sold()

    def num_sold(self) -> int:
        return TransactionItem.objects.filter(transaction__time_paid__isnull=False, item=self).count()

    @staticmethod
    def items_available() -> QuerySet["StoreItem"]:
        return (
            StoreItem.objects.filter(max__gt=0, available=True)
            .filter(Q(event__isnull=True) | Q(event__hidden=False))
            .order_by("sort_index")
        )

    @staticmethod
    def items_visible(secret_key: str | None = None) -> QuerySet["StoreItem"]:
        """Returns items visible in the store. May return additional items if
        the user has said the magic word."""
        return (
            StoreItem.objects.filter(max__gt=0, available=True)
            .filter(Q(event__isnull=True) | Q(event__hidden=False))
            .filter(Q(is_secret=False) | Q(secret_key=secret_key))
            .order_by("sort_index")
        )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "tuote"
        verbose_name_plural = "tuotteet"


class StoreItemVariant(models.Model):
    item = models.ForeignKey(StoreItem, on_delete=models.CASCADE)
    name = models.CharField("Tuotevariantin nimi", max_length=32, blank=False, null=False)

    def __str__(self) -> str:
        return "{}: {}".format(self.item.name, self.name)

    class Meta:
        verbose_name = "tuotevariantti"
        verbose_name_plural = "tuotevariantit"


class StoreTransaction(models.Model):
    token = models.CharField(
        "Palvelutunniste", help_text="Maksupalvelun maksukohtainen tunniste", max_length=255
    )
    time_created = models.DateTimeField("Luontiaika", null=True, blank=True, db_index=True)
    time_paid = models.DateTimeField("Maksun varmistumisaika", null=True, blank=True)
    time_pending = models.DateTimeField("Maksun maksuaika", null=True, blank=True)
    time_cancelled = models.DateTimeField("Peruutusaika", null=True, blank=True)
    payment_method_name = models.CharField(
        "Maksutapa", help_text="Tapa jolla tilaus maksettiin", max_length=32, blank=True, default=""
    )
    key = models.CharField(
        "Avain", max_length=40, unique=True, help_text="Paikallinen maksukohtainen tunniste"
    )
    firstname = models.CharField("Etunimi", max_length=64)
    lastname = models.CharField("Sukunimi", max_length=64)
    company = models.CharField("Yritys", max_length=128, blank=True)
    email = models.EmailField(
        "Sähköposti",
        max_length=255,
        help_text="Sähköpostiosoitteen on oltava toimiva, sillä liput ja tuotteiden lunastukseen "
        "tarvittavat koodit lähetetään sinne.",
    )
    telephone = models.CharField("Puhelinnumero", max_length=64, blank=True)
    mobile = models.CharField("Matkapuhelin", max_length=64, blank=True)
    street = models.CharField(
        "Katuosoite", max_length=128, help_text="Katusoite tarvitaan maksupalvelun vaatimuksesta."
    )
    postalcode = models.CharField("Postinumero", max_length=16)
    city = models.CharField("Postitoimipaikka", max_length=64)
    country = CountryField(verbose_name="Maa", default="FI")
    information = models.TextField(
        "Lisätiedot",
        help_text="Mikäli tilaukseen kuuluu T-paitoja, määritä niiden koot tässä.",
        blank=True,
    )

    @property
    def is_paid(self) -> bool:
        return self.time_paid is not None

    @property
    def is_cancelled(self) -> bool:
        return self.time_cancelled is not None

    @property
    def is_pending(self) -> bool:
        return self.time_pending is not None

    @property
    def is_delivered(self) -> bool:
        for item in self.get_transaction_items():
            if not item.is_delivered:
                return False
        return True

    @property
    def qr_code_path(self) -> str:
        return reverse("store:ta_view", kwargs={"transaction_key": self.key})

    @property
    def full_name(self) -> str:
        return "{} {}".format(self.firstname, self.lastname)

    def get_status_text(self) -> str:
        if self.is_cancelled:
            return "Peruutettu"
        if self.is_delivered:
            return "Toimitettu"
        if self.is_paid:
            return "Maksettu"
        if self.is_pending:
            return "Vireillä"
        return "Tuotteet valittu"

    def get_total_price(self) -> Decimal:
        ret = Decimal("0")
        for item in TransactionItem.objects.filter(transaction=self):
            ret += item.purchase_price
        return ret

    def get_transaction_items(self) -> QuerySet["TransactionItem"]:
        return TransactionItem.objects.filter(transaction=self)

    def get_distinct_store_items_and_prices(
        self,
    ) -> list[tuple[StoreItem, StoreItemVariant | None, Decimal]]:
        """
        We find the unique item groups here. Because in database we have all the bought items as individual
        items, we need to group them up for payment service and receipt. This function handles that.
        """
        qs = self.get_transaction_items().order_by("item__name", "variant__name")
        unique_items = {(t_item.item_id, t_item.variant_id, t_item.purchase_price): t_item for t_item in qs}
        return [
            (
                transaction_item.item,
                transaction_item.variant,
                transaction_item.purchase_price,
            )
            for _, transaction_item in unique_items.items()
        ]

    def get_store_item_count(
        self,
        store_item: StoreItem,
        variant: StoreItemVariant | None = None,
        purchase_price: Decimal | None = None,
    ) -> int:
        """
        Gets transaction item by its linked store-item. You can also use item variant and purchase price to make the
        query more detailed.
        """
        q = TransactionItem.objects.filter(item=store_item, transaction=self)
        if variant:
            q = q.filter(variant=variant)
        if purchase_price:
            q = q.filter(purchase_price=purchase_price)
        return q.count()

    def __str__(self) -> str:
        return self.full_name

    class Meta:
        verbose_name = "transaktio"
        verbose_name_plural = "transaktiot"
        # permissions = (("view_storetransaction", "Can view store transactions"),)
        # default_permissions = ('add', 'change', 'delete',)


class StoreTransactionEvent(models.Model):
    """Data log for transaction events (such as when payment events arrive from payment processor)"""

    transaction = models.ForeignKey(StoreTransaction, on_delete=models.CASCADE)
    message = models.CharField("Tapahtuman viesti", max_length=255, null=False)
    data = models.JSONField("Tapahtuman data", null=True)
    created = models.DateTimeField("Luontiaika", null=False, default=timezone.now)

    @classmethod
    def log(cls, transaction: StoreTransaction, message: str, data: dict[str, Any]) -> None:
        obj = cls(transaction=transaction, message=message, data=data)
        obj.save()


class TransactionItem(models.Model):
    key = models.CharField("Avain", max_length=40, unique=True, help_text="Lippuavain")
    item = models.ForeignKey(StoreItem, verbose_name="Tuote", on_delete=models.PROTECT)
    variant = models.ForeignKey(
        StoreItemVariant, verbose_name="Tuotevariantti", null=True, on_delete=models.PROTECT
    )
    transaction = models.ForeignKey(StoreTransaction, verbose_name="Ostotapahtuma", on_delete=models.CASCADE)
    time_delivered = models.DateTimeField("Toimitusaika", null=True, blank=True)
    purchase_price = models.DecimalField(
        "Tuotteen hinta", help_text="Tuotteen hinta ostoshetkellä", max_digits=5, decimal_places=2
    )
    original_price = models.DecimalField(
        "Tuotteen alkuperäinen hinta",
        help_text="Tuotteen hinta ostoshetkellä ilman alennuksia",
        max_digits=5,
        decimal_places=2,
    )

    @property
    def is_delivered(self) -> bool:
        return self.time_delivered is not None

    @property
    def qr_code_path(self) -> str:
        return reverse("store:ti_view", kwargs={"item_key": self.key})

    def __str__(self) -> str:
        return "{} for {}".format(self.item.name, self.transaction.full_name)

    class Meta:
        verbose_name = "transaktiotuote"
        verbose_name_plural = "transaktiotuotteet"


class Receipt(models.Model):
    transaction = models.ForeignKey(StoreTransaction, on_delete=models.SET_NULL, null=True, default=None)
    subject = models.CharField("Aihe", max_length=256)
    mail_to = models.CharField("Vastaanottajan osoite", max_length=256)
    mail_from = models.CharField("Lähettäjän osoite", max_length=256)
    sent = models.DateTimeField("Lähetysaika", default=None, null=True)
    params = models.TextField("Lähetysparametrit", default=None, null=True)
    content = models.TextField("Kuitin sisältö", default=None, null=True)

    def __str__(self) -> str:
        return "{}: {}".format(self.mail_to, self.subject)

    @property
    def is_sent(self) -> bool:
        return self.sent is not None

    @classmethod
    def create(
        cls,
        mail_to: str,
        mail_from: str,
        subject: str,
        params: ReceiptParams,
        transaction: StoreTransaction | None = None,
    ) -> "Receipt":
        # First, save header information and save so that we get a receipt ID
        r = cls()
        r.transaction = transaction
        r.subject = subject
        r.mail_to = mail_to
        r.mail_from = mail_from
        r.save()

        # Next, set receipt id for receipt, and generate params and contents.
        params.receipt_number(r.id)
        r.params = params.get_json()
        r.content = params.get_body()
        r.save()

        # Return newly created object for use, eg. for calling send()
        return r

    def send(self) -> None:
        if self.content is None:
            raise ValueError("Cannot send receipt without content")
        self.sent = timezone.now()
        send_mail(self.subject, self.content, self.mail_from, (self.mail_to,))
        self.save()

    class Meta:
        verbose_name = "kuitti"
        verbose_name_plural = "kuitit"


auditlog.register(StoreItem)
auditlog.register(StoreItemVariant)
auditlog.register(StoreTransaction)
auditlog.register(StoreTransactionEvent)
auditlog.register(TransactionItem)
auditlog.register(Receipt)
