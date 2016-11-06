# -*- coding: utf-8 -*-

from django.db import models
from Instanssi.kompomaatti.models import Event


class OtherVideoCategory(models.Model):
    event = models.ForeignKey(Event, verbose_name='Tapahtuma')
    name = models.CharField('Nimi', max_length=64, help_text='Kategorian nimi')

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = "videokategoria"
        verbose_name_plural = "videokategoriat"


class OtherVideo(models.Model):
    category = models.ForeignKey(OtherVideoCategory, verbose_name='Kategoria')
    name = models.CharField('Nimi', max_length=64, help_text='Videon nimi.')
    description = models.TextField('Kuvaus', help_text='Videon kuvaus.')
    youtube_url = models.URLField('Youtube URL', help_text="Linkki teoksen Youtube-versioon.", blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = "muu video"
        verbose_name_plural = "muut videot"
