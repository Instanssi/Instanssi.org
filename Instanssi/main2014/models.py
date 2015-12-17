# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class ToimistoJahti(models.Model):
    key = models.CharField(
        u'Avain', max_length=10, help_text=u"Avain", unique=True)
    help = models.TextField(
        u'Ohje', help_text=u'Ohjeteksti')
    
    def __unicode__(self):
        if len(self.help) > 15:
            return self.key + u': ' + self.help[:15] + u' ...'
        else:
            return self.key + u': ' + self.help
        
    class Meta:
        verbose_name = u"jahtitehtava"
        verbose_name_plural = u"jahtitehtavat"


class ToimistoSuoritus(models.Model):
    user = models.ForeignKey(
        User, verbose_name=u'Käyttäjä')
    nick = models.CharField(
        u'Tunnusnimi', max_length=32, help_text=u"Agentin tunnusnimi", unique=True)
    time = models.DateTimeField(
        u'Suoritusaika', help_text=u"Aika, jolloin agentti merkkasi tehtävän suoritetuksi")
    
    def __unicode__(self):
        return self.nick
    
    class Meta:
        verbose_name = u"toimistosuoritus"
        verbose_name_plural = u"toimistosuoritukset"
