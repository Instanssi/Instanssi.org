# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from Instanssi.kompomaatti.models import Event
from Instanssi.store.models import StoreItem, StoreTransaction

class Ticket(models.Model):
    transaction = models.ForeignKey(StoreTransaction, verbose_name=u'Ostotapahtuma', null=True, blank=True)
    storeitem = models.ForeignKey(StoreItem, verbose_name=u'Kauppatavara')
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    key = models.CharField(u'Avain', max_length=40, help_text=u'Lippuavain')
    used = models.BooleanField(u'Käytetty', default=False, help_text=u'Lippu on käytetty')
    
    def __unicode__(self):
        return self.key

    class Meta:
        verbose_name = u"lippu"
        verbose_name_plural = u"liput"
        
try:
    admin.site.register(Ticket)
except:
    pass