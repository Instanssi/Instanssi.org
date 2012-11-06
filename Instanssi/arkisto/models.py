# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from Instanssi.kompomaatti.models import Event

class OtherVideoCategory(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    name = models.CharField(u'Nimi', max_length=64, help_text=u'Kategorian nimi')

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name=u"videokategoria"
        verbose_name_plural=u"videokategoriat"

class OtherVideo(models.Model):
    category = models.ForeignKey(OtherVideoCategory, verbose_name=u'Kategoria')
    name = models.CharField(u'Nimi', max_length=64, help_text=u'Videon nimi.')
    description = models.TextField(u'Kuvaus', help_text=u'Videon kuvaus.')
    youtube_url = models.URLField(u'Youtube URL', help_text=u"Linkki teoksen Youtube-versioon.", blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name=u"muu video"
        verbose_name_plural=u"muut videot"

try:
    admin.site.register(OtherVideoCategory)
    admin.site.register(OtherVideo)
except:
    pass
