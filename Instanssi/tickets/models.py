# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from Instanssi.kompomaatti.models import Event
from Instanssi.store.models import StoreItem, StoreTransaction


class Ticket(models.Model):
    transaction = models.ForeignKey(StoreTransaction, verbose_name=u'Ostotapahtuma', null=True, blank=True)
    storeitem = models.ForeignKey(StoreItem, verbose_name=u'Kauppatavara')
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    key = models.CharField(u'Avain', max_length=40, unique=True, help_text=u'Lippuavain')
    used = models.BooleanField(u'Käytetty', default=False, help_text=u'Lippu on käytetty')
    owner_firstname = models.CharField(u'Etunimi', max_length=64, help_text=u'Lipun omistajan etunimi')
    owner_lastname = models.CharField(u'Sukunimi', max_length=64, help_text=u'Lipun omistajan sukunimi')
    owner_email = models.CharField(u'Sähköposti', max_length=255, help_text=u'Lipun omistajan sähköposti', blank=True)

    def __unicode__(self):
        return u'%s %s (%s)' % (self.owner_firstname, self.owner_lastname, self.key)

    @staticmethod
    def tickets_for_transaction(transaction):
        return Ticket.objects.filter(transaction=transaction)

    @property
    def qr_code(self):
        return self.key

    class Meta:
        verbose_name = u"lippu"
        verbose_name_plural = u"liput"

try:
    admin.site.register(Ticket)
except:
    pass
