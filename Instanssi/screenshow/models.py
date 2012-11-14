# -*- coding: utf-8 -*-

from django.db import models
from Instanssi.kompomaatti.models import Event

class Sponsor(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    name = models.CharField(u'Nimi', max_length=64, help_text=u'Sponsorin nimi')
    logo = models.ImageField(u'Kuva', upload_to='screen/sponsorlogos/', help_text=u"Sponsorin logo", blank=True)

class Message(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    show_start = models.DateTimeField(u'Alkuaika', help_text=u'Viestin näyttäminen alkaa')
    show_end = models.DateTimeField(u'Loppuaika', help_text=u'Viestin näyttäminen päättyy')
    text = models.TextField(u'Viesti', help_text=u'Viestin leipäteksti. Katso ettei tästä tule liian pitkä.')
    
class IRCMessage(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    date = models.DateTimeField(u'Aika')
    nick = models.CharField(u'Nimimerkki', max_length=64)
    message = models.TextField('Viesti')