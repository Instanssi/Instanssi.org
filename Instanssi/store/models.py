# -*- coding: utf-8 -*-

from django.db import models
from django_countries import CountryField
from django.db.models import Sum
from django.contrib import admin
from datetime import datetime
from Instanssi.kompomaatti.models import Event
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class StoreItem(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma', help_text=u'Tapahtuma johon tuote liittyy.', blank=True, null=True)
    name = models.CharField(u'Tuotteen nimi', help_text=u'Tuotteen lyhyt nimi.', max_length=255)
    description = models.TextField(u'Tuotteen kuvaus', help_text=u'Tuotteen pitkä kuvaus.')
    price = models.FloatField(u'Tuotteen hinta', help_text=u'Tuotteen hinta euroissa.')
    max = models.IntegerField(u'Kappaletta saatavilla', help_text=u'Kuinka monta kappaletta on ostettavissa ennen myynnin lopettamista.')
    available = models.BooleanField(u'Ostettavissa', default=False, help_text=u'Ilmoittaa, näkyykö tuote kaupassa.')
    imagefile_original = models.ImageField(u'Tuotekuva', upload_to='store/images/', help_text=u"Edustava kuva tuotteelle.", blank=True, null=True)
    imagefile_thumbnail = ImageSpecField([ResizeToFill(64, 64)], image_field='imagefile_original', format='PNG')
    max_per_order = models.IntegerField(u'Maksimi per tilaus', default=10, help_text=u'Kuinka monta kappaletta voidaan ostaa kerralla.')
    DELIVERY_CHOICES=(
        (0, u'Ei toimitusta'),
        (1, u'Lippu'),
        (2, u'Postitus'),
        (3, u'Toimitus tapahtumassa')
    )
    delivery_type = models.IntegerField(u'Toimitustyyppi', default=0, choices=DELIVERY_CHOICES, help_text=u'Miten tuote toimitetaan asiakkaalle')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"tuote"
        verbose_name_plural = u"tuotteet"

    def num_available(self):
        return min(self.max - self.sold(), self.max_per_order)

    def sold(self):
        res = TransactionItem.objects.filter(
            transaction__time_paid__isnull=False,
            item=self
        ).aggregate(Sum('amount'))
        if res['amount__sum'] is None:
            return 0
        return res['amount__sum']

    @staticmethod
    def items_for_event(event_id):
        return StoreItem.objects.filter(max__gt=0, available=True,
                                        event_id=event_id)


class StoreTransaction(models.Model):
    token = models.CharField(u'Palvelutunniste', help_text=u'Maksupalvelun maksukohtainen tunniste', max_length=255)
    time_created = models.DateTimeField(u'Luontiaika', null=True, blank=True)
    time_paid = models.DateTimeField(u'Maksuaika', null=True, blank=True)
    key = models.CharField(u'Avain', max_length=40, unique=True, help_text=u'Paikallinen maksukohtainen tunniste')
    firstname = models.CharField(u'Etunimi', max_length=64)
    lastname = models.CharField(u'Sukunimi', max_length=64)
    company = models.CharField(u'Yritys', max_length=128, blank=True)
    email = models.EmailField(u'Sähköposti', max_length=255)
    telephone = models.CharField(u'Puhelinnumero', max_length=64, blank=True)
    mobile = models.CharField(u'Matkapuhelin', max_length=64, blank=True)
    street = models.CharField(u'Katuosoite', max_length=128)
    postalcode = models.CharField(u'Postinumero', max_length=16)
    city = models.CharField(u'Postitoimipaikka', max_length=64)
    country = CountryField(u'Maa', default='FI')

    def __unicode__(self):
        return u'%s %s' % (self.firstname, self.lastname)

    @property
    def paid(self):
        return self.time_paid is not None

    def total(self):
        ret = 0.0
        for item in TransactionItem.objects.filter(transaction=self):
            ret += item.total()
        return ret

    class Meta:
        verbose_name = u"transaktio"
        verbose_name_plural = u"transaktiot"
        permissions = (("view_storetransaction", "Can view store transactions"),)


class TransactionItem(models.Model):
    item = models.ForeignKey(StoreItem, verbose_name=u'Tuote')
    transaction = models.ForeignKey(StoreTransaction, verbose_name=u'Ostotapahtuma')
    amount = models.IntegerField(u'Määrä')

    def total(self):
        return self.amount * self.item.price

    def __unicode__(self):
        return u'%s for %s %s' % (self.item.name, self.transaction.firstname, self.transaction.lastname)

    class Meta:
        verbose_name = u"transaktiotuote"
        verbose_name_plural = u"transaktiotuotteet"

try:
    admin.site.register(StoreItem)
    admin.site.register(StoreTransaction)
    admin.site.register(TransactionItem)
except:
    pass
