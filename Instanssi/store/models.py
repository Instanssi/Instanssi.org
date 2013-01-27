# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Sum
from django.contrib import admin
from datetime import datetime
from Instanssi.kompomaatti.models import Event
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class StoreItem(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma', blank=True, null=True)
    name = models.CharField(u'Tuotteen nimi', max_length=255)
    description = models.TextField(u'Tuotteen kuvaus')
    price = models.FloatField(u'Tuotteen hinta')
    max = models.IntegerField(u'Kappaletta saatavilla')
    available = models.BooleanField(u'Ostettavissa', default=False)
    imagefile_original = models.ImageField(u'Tuotekuva', upload_to='store/images/', help_text=u"Edustava kuva tuotteelle.", blank=True, null=True)
    imagefile_thumbnail = ImageSpecField([ResizeToFill(64, 64)], image_field='imagefile_original', format='PNG')
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name=u"tuote"
        verbose_name_plural=u"tuotteet"
    
    def sold(self):
        res = TransactionItem.objects.filter(transaction__paid=1, item=self).aggregate(Sum('amount'))
        if res['amount__sum'] == None:
            return 0
        return res['amount__sum']

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
    
    def __unicode__(self):
        return u'%s %s' % (self.firstname, self.lastname)
    
    def total(self):
        ret = 0.0
        for item in TransactionItem.objects.filter(transaction=self):
            ret += item.total()
        return ret
    
    class Meta:
        verbose_name=u"transaktio"
        verbose_name_plural=u"transaktiot"
        permissions = (("view_storetransaction", "Can view store transactions"),)
    
class TransactionItem(models.Model):
    item = models.ForeignKey(StoreItem, verbose_name=u'Tuote')
    transaction = models.ForeignKey(StoreTransaction, verbose_name=u'Ostotapahtuma')
    amount = models.IntegerField(u'Ostettu')
    
    def total(self):
        return self.amount * self.item.price
    
    def __unicode__(self):
        return u'%s for %s %s' % (self.item.name, self.transaction.firstname, self.transaction.lastname)

    class Meta:
        verbose_name=u"transaktiotuote"
        verbose_name_plural=u"transaktiotuotteet"

try:
    admin.site.register(StoreItem)
    admin.site.register(StoreTransaction)
    admin.site.register(TransactionItem)
except:
    pass
