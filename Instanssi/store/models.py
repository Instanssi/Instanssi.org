# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from datetime import datetime
from Instanssi.kompomaatti.models import Event


class StoreItem(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma', blank=True,
                              null=True)
    name = models.CharField(u'Tuotteen nimi', max_length=255)
    description = models.TextField(u'Tuotteen kuvaus')
    price = models.FloatField(u'Tuotteen hinta')
    max = models.IntegerField(u'Kappaletta saatavilla')
    available = models.BooleanField(u'Ostettavissa', default=False)

    def __unicode__(self):
        return self.name

    @staticmethod
    def itemsForEvent(event_id):
        return StoreItem.objects.filter(max__gt=0, available=True,
                                        event_id=event_id)


class StoreTransaction(models.Model):
    token = models.CharField(u'Palvelutunniste', max_length=255)
    time = models.DateTimeField(u'Aika')
    paid = models.BooleanField(u'Maksettu')

    firstname = models.CharField(u'Etunimi', max_length=64)
    lastname = models.CharField(u'Sukunimi', max_length=64)
    company = models.CharField(u'Yritys', max_length=128, blank=True)
    email = models.EmailField(u'Sähköposti', max_length=255)
    telephone = models.CharField(u'Puhelinnumero', max_length=64, blank=True)
    mobile = models.CharField(u'Matkapuhelin', max_length=64, blank=True)
    street = models.CharField(u'Katuosoite', max_length=128)
    postalcode = models.CharField(u'Postinumero', max_length=16)
    city = models.CharField(u'Postitoimipaikka', max_length=64)
    country = models.CharField(u'Maa', max_length=2)

    def _fullname(self):
        return '%s %s' % (self.firstname, self.lastname)

    def __unicode__(self):
        return "%s %s" % (self._fullname(), self.time)


class TransactionItem(models.Model):
    item = models.ForeignKey(StoreItem, verbose_name=u'Tuote')
    transaction = models.ForeignKey(StoreTransaction,
                                    verbose_name=u'Ostotapahtuma')
    amount = models.IntegerField(u'Määrä')

    def __unicode__(self):
        return "%s (%i) for %s" % (self.item.name, self.amount,
                                   self.transaction.__unicode__())

try:
    admin.site.register(StoreItem)
    admin.site.register(StoreTransaction)
    admin.site.register(TransactionItem)
except:
    pass
