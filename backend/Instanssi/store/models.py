import os
from datetime import datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from auditlog.registry import auditlog
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q, QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from Instanssi.common.file_handling import clean_filename, generate_upload_path
from Instanssi.common.html.fields import SanitizedHtmlField
from Instanssi.kompomaatti.models import Event
from Instanssi.store.utils.receipt import ReceiptParams


def generate_image_path(item: "StoreItem", filename: str) -> str:
    slug = clean_filename(Path(filename).stem)
    dt = datetime.combine(item.event.date, time(0, 0, 0, 0))
    return generate_upload_path(
        original_file=filename,
        path=settings.MEDIA_STORE_IMAGES,
        slug=slug,
        timestamp=dt,
    )


class StoreItem(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=_("Event"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    name = models.CharField(_("Name"), max_length=255)
    description = SanitizedHtmlField(_("Description"))
    price = models.DecimalField(_("Price"), max_digits=5, decimal_places=2)
    max = models.IntegerField(_("Available quantity"))
    available = models.BooleanField(_("Available for purchase"), default=False)
    imagefile_original = models.ImageField(
        _("Product image"),
        max_length=255,
        upload_to=generate_image_path,
        blank=True,
        null=True,
    )
    imagefile_thumbnail = ImageSpecField([ResizeToFill(64, 64)], source="imagefile_original", format="PNG")
    max_per_order = models.IntegerField(_("Max per order"), default=10)
    sort_index = models.IntegerField(_("Sort index"), default=0)
    discount_amount = models.IntegerField(
        _("Discount threshold"),
        default=-1,
        help_text=_("Minimum quantity for discount (-1 = disabled)"),
    )
    discount_percentage = models.IntegerField(_("Discount percentage"), default=0)
    is_ticket = models.BooleanField(_("Is ticket product"), default=False)
    is_secret = models.BooleanField(_("Is secret product"), default=False)
    secret_key = models.CharField(_("Secret key"), blank=True, max_length=255)

    def is_discount_available(self) -> bool:
        """Returns True if a discount exists for this item."""
        return self.discount_amount >= 0

    @property
    def variants(self) -> QuerySet:
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
    def items_available() -> QuerySet:
        return (
            StoreItem.objects.filter(max__gt=0, available=True)
            .filter(Q(event__isnull=True) | Q(event__hidden=False))
            .order_by("sort_index")
        )

    @staticmethod
    def items_visible(secret_key: Optional[str] = None) -> QuerySet:
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


class StoreItemVariant(models.Model):
    item = models.ForeignKey(StoreItem, on_delete=models.CASCADE)
    name = models.CharField(_("Name"), max_length=32, blank=False, null=False)

    def __str__(self) -> str:
        return "{}: {}".format(self.item.name, self.name)


class StoreTransaction(models.Model):
    token = models.CharField(_("Service token"), max_length=255)
    time_created = models.DateTimeField(_("Created"), null=True, blank=True)
    time_paid = models.DateTimeField(_("Paid"), null=True, blank=True)
    time_pending = models.DateTimeField(_("Pending"), null=True, blank=True)
    time_cancelled = models.DateTimeField(_("Cancelled"), null=True, blank=True)
    payment_method_name = models.CharField(_("Payment method"), max_length=32, blank=True, default="")
    key = models.CharField(_("Key"), max_length=40, unique=True)
    firstname = models.CharField(_("First name"), max_length=64)
    lastname = models.CharField(_("Last name"), max_length=64)
    company = models.CharField(_("Company"), max_length=128, blank=True)
    email = models.EmailField(_("Email"), max_length=255)
    telephone = models.CharField(_("Telephone"), max_length=64, blank=True)
    mobile = models.CharField(_("Mobile"), max_length=64, blank=True)
    street = models.CharField(_("Street address"), max_length=128)
    postalcode = models.CharField(_("Postal code"), max_length=16)
    city = models.CharField(_("City"), max_length=64)
    country = CountryField(_("Country"), default="FI")
    information = models.TextField(_("Additional information"), blank=True)

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
            return _("Cancelled")
        if self.is_delivered:
            return _("Delivered")
        if self.is_paid:
            return _("Paid")
        if self.is_pending:
            return _("Pending")
        return _("Items selected")

    def get_total_price(self) -> Decimal:
        ret = Decimal("0")
        for item in TransactionItem.objects.filter(transaction=self):
            ret += item.purchase_price
        return ret

    def get_transaction_items(self) -> QuerySet:
        return TransactionItem.objects.filter(transaction=self)

    def get_distinct_store_items_and_prices(
        self,
    ) -> List[Tuple[StoreItem, Optional[StoreItemVariant], Decimal]]:
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
        variant: Optional[StoreItemVariant] = None,
        purchase_price: Optional[Decimal] = None,
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


class StoreTransactionEvent(models.Model):
    """Data log for transaction events (such as when payment events arrive from payment processor)"""

    transaction = models.ForeignKey(StoreTransaction, on_delete=models.CASCADE)
    message = models.CharField(_("Message"), max_length=255, null=False)
    data = models.JSONField(_("Data"), null=True)
    created = models.DateTimeField(_("Created"), null=False, default=timezone.now)

    @classmethod
    def log(cls, transaction: StoreTransaction, message: str, data: Dict) -> None:
        obj = cls(transaction=transaction, message=message, data=data)
        obj.save()


class TransactionItem(models.Model):
    key = models.CharField(_("Key"), max_length=40, unique=True)
    item = models.ForeignKey(StoreItem, verbose_name=_("Item"), on_delete=models.PROTECT)
    variant = models.ForeignKey(
        StoreItemVariant, verbose_name=_("Variant"), null=True, on_delete=models.PROTECT
    )
    transaction = models.ForeignKey(
        StoreTransaction, verbose_name=_("Transaction"), on_delete=models.CASCADE
    )
    time_delivered = models.DateTimeField(_("Delivered"), null=True, blank=True)
    purchase_price = models.DecimalField(_("Purchase price"), max_digits=5, decimal_places=2)
    original_price = models.DecimalField(_("Original price"), max_digits=5, decimal_places=2)

    @property
    def is_delivered(self) -> bool:
        return self.time_delivered is not None

    @property
    def qr_code_path(self) -> str:
        return reverse("store:ti_view", kwargs={"item_key": self.key})

    def __str__(self) -> str:
        return "{} for {}".format(self.item.name, self.transaction.full_name)


class Receipt(models.Model):
    transaction = models.ForeignKey(StoreTransaction, on_delete=models.SET_NULL, null=True, default=None)
    subject = models.CharField(_("Subject"), max_length=256)
    mail_to = models.CharField(_("Recipient"), max_length=256)
    mail_from = models.CharField(_("Sender"), max_length=256)
    sent = models.DateTimeField(_("Sent"), default=None, null=True)
    params = models.TextField(_("Parameters"), default=None, null=True)
    content = models.TextField(_("Content"), default=None, null=True)

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
        transaction: Optional[StoreTransaction] = None,
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
        self.sent = timezone.now()
        send_mail(self.subject, self.content, self.mail_from, (self.mail_to,))
        self.save()


auditlog.register(StoreItem)
auditlog.register(StoreItemVariant)
auditlog.register(StoreTransaction)
auditlog.register(StoreTransactionEvent)
auditlog.register(TransactionItem)
auditlog.register(Receipt)
