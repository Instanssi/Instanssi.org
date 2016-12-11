# -*- coding: utf-8 -*-

import os
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.db import models
from django_countries.fields import CountryField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from Instanssi.kompomaatti.models import Event
from Instanssi.common.misc import get_url


class StoreItem(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name='Tapahtuma',
        help_text='Tapahtuma johon tuote liittyy.',
        blank=True,
        null=True)
    name = models.CharField(
        'Tuotteen nimi',
        help_text='Tuotteen lyhyt nimi.',
        max_length=255)
    description = models.TextField(
        'Tuotteen kuvaus',
        help_text='Tuotteen pitkä kuvaus.')
    price = models.DecimalField(
        'Tuotteen hinta',
        help_text='Tuotteen hinta.',
        max_digits=5,
        decimal_places=2)
    max = models.IntegerField(
        'Kappaletta saatavilla',
        help_text='Kuinka monta kappaletta on ostettavissa ennen myynnin lopettamista.')
    available = models.BooleanField(
        'Ostettavissa',
        default=False,
        help_text='Ilmoittaa, näkyykö tuote kaupassa.')
    imagefile_original = models.ImageField(
        'Tuotekuva',
        upload_to='store/images/',
        help_text="Edustava kuva tuotteelle.", blank=True, null=True)
    imagefile_thumbnail = ImageSpecField(
        [ResizeToFill(64, 64)],
        source='imagefile_original',
        format='PNG')
    max_per_order = models.IntegerField(
        'Maksimi per tilaus',
        default=10,
        help_text='Kuinka monta kappaletta voidaan ostaa kerralla.')
    sort_index = models.IntegerField(
        'Järjestysarvo',
        default=0,
        help_text='Tuotteet esitetään kaupassa tämän luvun mukaan järjestettynä, pienempilukuiset ensin.')
    discount_amount = models.IntegerField(
        'Alennusmäärä',
        default=-1,
        help_text='Pienin määrä tuotteita joka oikeuttaa alennukseen (-1 = ei mitään)')
    discount_percentage = models.IntegerField(
        'Alennusprosentti',
        default=0,
        help_text='Alennuksen määrä prosentteina kun tuotteiden määrä saavuttaa alennusmäärän.')

    def is_discount_available(self):
        """Returns True if a discount exists for this item."""
        return self.discount_amount >= 0

    @property
    def variants(self):
        """ Returns a queryset with the available item variants """
        return StoreItemVariant.objects.filter(item=self)

    def get_discount_factor(self):
        """Gets the potential discount factor, for views/templates/JS.

        Decimal arithmetic is used for actual price calculations."""
        return (100.0 - self.discount_percentage) / 100.0

    def is_discount_enabled(self, amount):
        """Returns True if discount applies to a specific quantity of this."""
        return self.is_discount_available() and amount >= self.discount_amount

    def image_available(self):
        return os.path.exists(self.imagefile_original.name)

    def get_discounted_unit_price(self, amount):
        """Returns decimal price of item considering any quantity discount."""
        if self.is_discount_enabled(amount):
            factor = (Decimal(100) - Decimal(self.discount_percentage)) / 100
            price = self.price * factor
        else:
            price = self.price
        # If we need to consider rounding direction, this might be the place.
        # Pass "rounding=METHOD" as second argument.
        return price.quantize(Decimal('0.01'))

    def get_discounted_subtotal(self, amount):
        """Returns decimal subtotal for a specific number of items, considering
        any quantity discount."""
        return self.get_discounted_unit_price(amount) * amount

    def num_available(self):
        return min(self.max - self.num_sold(), self.max_per_order)

    def num_in_store(self):
        return self.max - self.num_sold()

    def num_sold(self):
        return TransactionItem.objects.filter(
            transaction__time_paid__isnull=False,
            item=self
        ).count()

    @staticmethod
    def items_available():
        return StoreItem.objects.filter(max__gt=0, available=True).order_by('sort_index')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "tuote"
        verbose_name_plural = "tuotteet"


class StoreItemVariant(models.Model):
    item = models.ForeignKey(StoreItem)
    name = models.CharField('Tuotevariantin nimi', max_length=32, blank=False, null=False)

    def __str__(self):
        return "{}: {}".format(self.item.name, self.name)

    class Meta:
        verbose_name = "tuotevariantti"
        verbose_name_plural = "tuotevariantit"


class StoreTransaction(models.Model):
    token = models.CharField(
        'Palvelutunniste',
        help_text='Maksupalvelun maksukohtainen tunniste',
        max_length=255)
    time_created = models.DateTimeField(
        'Luontiaika',
        null=True,
        blank=True)
    time_paid = models.DateTimeField(
        'Maksun varmistumisaika',
        null=True,
        blank=True)
    time_pending = models.DateTimeField(
        'Maksun maksuaika',
        null=True,
        blank=True)
    time_cancelled = models.DateTimeField(
        'Peruutusaika',
        null=True,
        blank=True)
    payment_method_name = models.CharField(
        'Maksutapa',
        help_text='Tapa jolla tilaus maksettiin',
        max_length=32,
        blank=True,
        default='')
    key = models.CharField(
        'Avain',
        max_length=40,
        unique=True,
        help_text='Paikallinen maksukohtainen tunniste')
    firstname = models.CharField(
        'Etunimi',
        max_length=64)
    lastname = models.CharField(
        'Sukunimi',
        max_length=64)
    company = models.CharField\
        ('Yritys',
         max_length=128,
         blank=True)
    email = models.EmailField(
        'Sähköposti',
        max_length=255,
        help_text='Sähköpostiosoitteen on oltava toimiva, sillä liput ja tuotteiden lunastukseen '
                  'tarvittavat koodit lähetetään sinne.')
    telephone = models.CharField(
        'Puhelinnumero',
        max_length=64,
        blank=True)
    mobile = models.CharField(
        'Matkapuhelin',
        max_length=64,
        blank=True)
    street = models.CharField(
        'Katuosoite',
        max_length=128,
        help_text='Katusoite tarvitaan maksupalvelun vaatimuksesta.')
    postalcode = models.CharField(
        'Postinumero',
        max_length=16)
    city = models.CharField(
        'Postitoimipaikka',
        max_length=64)
    country = CountryField(
        'Maa',
        default='FI')
    information = models.TextField(
        'Lisätiedot',
        help_text='Mikäli tilaukseen kuuluu T-paitoja, määritä niiden koot tässä.',
        blank=True)

    @property
    def is_paid(self):
        return self.time_paid is not None

    @property
    def is_cancelled(self):
        return self.time_cancelled is not None

    @property
    def is_pending(self):
        return self.time_pending is not None

    @property
    def is_delivered(self):
        for item in self.get_transaction_items():
            if not item.is_delivered:
                return False
        return True

    @property
    def qr_code(self):
        return get_url(reverse('store:ta_view', kwargs={'transaction_key': self.key}))

    @property
    def full_name(self):
        return '{} {}'.format(self.firstname, self.lastname)

    def get_status_text(self):
        if self.is_cancelled:
            return 'Peruutettu'
        if self.is_delivered:
            return 'Toimitettu'
        if self.is_paid:
            return 'Maksettu'
        if self.is_pending:
            return 'Vireillä'
        return 'Tuotteet valittu'

    def get_total_price(self):
        ret = 0
        for item in TransactionItem.objects.filter(transaction=self):
            ret += item.purchase_price
        return ret

    def get_transaction_items(self):
        return TransactionItem.objects.filter(transaction=self)

    def get_distinct_storeitems_and_prices(self):
        """Returns a list of unique (StoreItem, price) tuples related to
        this transaction."""

        items = {}
        transaction_items = self.get_transaction_items().values_list('item', 'variant', 'purchase_price')
        for item, variant, price in transaction_items:
            if item not in items:
                items[item] = {}
            items[item][variant] = price

        item_list = []
        for item_key, variants in items.items():
            for variant_key, price in variants.items():
                item_list.append((
                    StoreItem.objects.get(pk=item_key),
                    StoreItemVariant.objects.get(pk=variant_key) if variant_key else None,
                    price
                ))
        return item_list

    def get_storeitem_count(self, store_item, variant=None):
        q = TransactionItem.objects.filter(item=store_item, transaction=self)
        if variant:
            q = q.filter(variant=variant)
        return q.count()

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "transaktio"
        verbose_name_plural = "transaktiot"
        permissions = (("view_storetransaction", "Can view store transactions"),)


class TransactionItem(models.Model):
    key = models.CharField(
        'Avain',
        max_length=40,
        unique=True,
        help_text='Lippuavain')
    item = models.ForeignKey(
        StoreItem,
        verbose_name='Tuote')
    variant = models.ForeignKey(
        StoreItemVariant,
        verbose_name='Tuotevariantti',
        null=True)
    transaction = models.ForeignKey(
        StoreTransaction,
        verbose_name='Ostotapahtuma')
    time_delivered = models.DateTimeField(
        'Toimitusaika',
        null=True,
        blank=True)
    purchase_price = models.DecimalField(
        'Tuotteen hinta',
        help_text='Tuotteen hinta ostoshetkellä',
        max_digits=5,
        decimal_places=2)
    original_price = models.DecimalField(
        'Tuotteen alkuperäinen hinta',
        help_text='Tuotteen hinta ostoshetkellä ilman alennuksia',
        max_digits=5,
        decimal_places=2)

    @property
    def is_delivered(self):
        return self.time_delivered is not None

    @property
    def qr_code(self):
        return get_url(reverse('store:ti_view', kwargs={'item_key': self.key}))

    def __str__(self):
        return '{} for {}'.format(self.item.name, self.transaction.full_name)

    class Meta:
        verbose_name = "transaktiotuote"
        verbose_name_plural = "transaktiotuotteet"
