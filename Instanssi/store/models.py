# -*- coding: utf-8 -*-

from decimal import Decimal
from django.core.urlresolvers import reverse
from django.db import models
from django_countries.fields import CountryField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from Instanssi.kompomaatti.models import Event
from common.misc import get_url


class StoreItem(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=u'Tapahtuma',
        help_text=u'Tapahtuma johon tuote liittyy.',
        blank=True,
        null=True)
    name = models.CharField(
        u'Tuotteen nimi',
        help_text=u'Tuotteen lyhyt nimi.',
        max_length=255)
    description = models.TextField(
        u'Tuotteen kuvaus',
        help_text=u'Tuotteen pitkä kuvaus.')
    price = models.DecimalField(
        u'Tuotteen hinta',
        help_text=u'Tuotteen hinta.',
        max_digits=5,
        decimal_places=2)
    max = models.IntegerField(
        u'Kappaletta saatavilla',
        help_text=u'Kuinka monta kappaletta on ostettavissa ennen myynnin lopettamista.')
    available = models.BooleanField(
        u'Ostettavissa',
        default=False,
        help_text=u'Ilmoittaa, näkyykö tuote kaupassa.')
    imagefile_original = models.ImageField(
        u'Tuotekuva',
        upload_to='store/images/',
        help_text=u"Edustava kuva tuotteelle.", blank=True, null=True)
    imagefile_thumbnail = ImageSpecField(
        [ResizeToFill(64, 64)],
        source='imagefile_original',
        format='PNG')
    max_per_order = models.IntegerField(
        u'Maksimi per tilaus',
        default=10,
        help_text=u'Kuinka monta kappaletta voidaan ostaa kerralla.')
    sort_index = models.IntegerField(
        u'Järjestysarvo',
        default=0,
        help_text=u'Tuotteet esitetään kaupassa tämän luvun mukaan järjestettynä, pienempilukuiset ensin.')
    discount_amount = models.IntegerField(
        u'Alennusmäärä',
        default=-1,
        help_text=u'Pienin määrä tuotteita joka oikeuttaa alennukseen (-1 = ei mitään)')
    discount_percentage = models.IntegerField(
        u'Alennusprosentti',
        default=0,
        help_text=u'Alennuksen määrä prosentteina kun tuotteiden määrä saavuttaa alennusmäärän.')

    def is_discount_available(self):
        """Returns True if a discount exists for this item."""
        return self.discount_amount >= 0

    def get_discount_factor(self):
        """Gets the potential discount factor, for views/templates/JS.

        Decimal arithmetic is used for actual price calculations."""
        return (100.0 - self.discount_percentage) / 100.0

    def is_discount_enabled(self, amount):
        """Returns True if discount applies to a specific quantity of this."""
        return self.is_discount_available() and amount >= self.discount_amount

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

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"tuote"
        verbose_name_plural = u"tuotteet"


class StoreTransaction(models.Model):
    token = models.CharField(
        u'Palvelutunniste',
        help_text=u'Maksupalvelun maksukohtainen tunniste',
        max_length=255)
    time_created = models.DateTimeField(
        u'Luontiaika',
        null=True,
        blank=True)
    time_paid = models.DateTimeField(
        u'Maksun varmistumisaika',
        null=True,
        blank=True)
    time_pending = models.DateTimeField(
        u'Maksun maksuaika',
        null=True,
        blank=True)
    time_cancelled = models.DateTimeField(
        u'Peruutusaika',
        null=True,
        blank=True)
    payment_method_name = models.CharField(
        u'Maksutapa',
        help_text=u'Tapa jolla tilaus maksettiin',
        max_length=32,
        blank=True,
        default=u'')
    key = models.CharField(
        u'Avain',
        max_length=40,
        unique=True,
        help_text=u'Paikallinen maksukohtainen tunniste')
    firstname = models.CharField(
        u'Etunimi',
        max_length=64)
    lastname = models.CharField(
        u'Sukunimi',
        max_length=64)
    company = models.CharField\
        (u'Yritys',
         max_length=128,
         blank=True)
    email = models.EmailField(
        u'Sähköposti',
        max_length=255,
        help_text=u'Sähköpostiosoitteen on oltava toimiva, sillä liput ja tuotteiden lunastukseen '
                  u'tarvittavat koodit lähetetään sinne.')
    telephone = models.CharField(
        u'Puhelinnumero',
        max_length=64,
        blank=True)
    mobile = models.CharField(
        u'Matkapuhelin',
        max_length=64,
        blank=True)
    street = models.CharField(
        u'Katuosoite',
        max_length=128,
        help_text=u'Katusoite tarvitaan maksupalvelun vaatimuksesta.')
    postalcode = models.CharField(
        u'Postinumero',
        max_length=16)
    city = models.CharField(
        u'Postitoimipaikka',
        max_length=64)
    country = CountryField(
        u'Maa',
        default='FI')
    information = models.TextField(
        u'Lisätiedot',
        help_text=u'Mikäli tilaukseen kuuluu T-paitoja, määritä niiden koot tässä.',
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
        return u'{} {}'.format(self.firstname, self.lastname)

    def get_status_text(self):
        if self.is_cancelled:
            return u'Peruutettu'
        if self.is_delivered:
            return u'Toimitettu'
        if self.is_paid:
            return u'Maksettu'
        if self.is_pending:
            return u'Vireillä'
        return u'Tuotteet valittu'

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
        # get (item-id, price) tuples
        items = self.get_transaction_items().values_list(
            'item', 'purchase_price').distinct()
        itemlist = []
        for key, price in items:
            # this isn't a performance issue with our database
            itemlist.append((StoreItem.objects.filter(pk=key).get(), price))
        return itemlist

    def get_storeitem_count(self, store_item):
        return TransactionItem.objects.filter(
            item=store_item, transaction=self).count()

    def __unicode__(self):
        return self.full_name

    class Meta:
        verbose_name = u"transaktio"
        verbose_name_plural = u"transaktiot"
        permissions = (("view_storetransaction", "Can view store transactions"),)


class TransactionItem(models.Model):
    key = models.CharField(
        u'Avain',
        max_length=40,
        unique=True,
        help_text=u'Lippuavain')
    item = models.ForeignKey(
        StoreItem,
        verbose_name=u'Tuote')
    transaction = models.ForeignKey(
        StoreTransaction,
        verbose_name=u'Ostotapahtuma')
    time_delivered = models.DateTimeField(
        u'Toimitusaika',
        null=True,
        blank=True)
    purchase_price = models.DecimalField(
        u'Tuotteen hinta',
        help_text=u'Tuotteen hinta ostoshetkellä',
        max_digits=5,
        decimal_places=2)
    original_price = models.DecimalField(
        u'Tuotteen alkuperäinen hinta',
        help_text=u'Tuotteen hinta ostoshetkellä ilman alennuksia',
        max_digits=5,
        decimal_places=2)

    @property
    def is_delivered(self):
        return self.time_delivered is not None

    @property
    def qr_code(self):
        return get_url(reverse('store:ti_view', kwargs={'item_key': self.key}))

    def __unicode__(self):
        return u'{} for {}'.format(self.item.name, self.transaction.full_name)

    class Meta:
        verbose_name = u"transaktiotuote"
        verbose_name_plural = u"transaktiotuotteet"
