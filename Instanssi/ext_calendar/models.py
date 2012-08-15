# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from Instanssi.kompomaatti.models import Event

class CalendarEvent(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    user = models.ForeignKey(User, verbose_name=u'Käyttäjä')
    start = models.DateTimeField(u'Alku', help_text=u'Tapahtuman alkamisaika.')
    end = models.DateTimeField(u'Loppe', help_text=u'Tapahtuman loppumisaika.', blank=True)
    description = models.TextField(u'Kuvaus', help_text=u'Tapahtuman kuvaus.', blank=True)
    title = models.CharField(u'Otsikko', help_text=u'Lyhyt otsikko.', max_length=32)
    image_original = models.ImageField(u'Kuva', upload_to='calendar/images/', help_text=u"Kuva tapahtumalle.", blank=True)
    image_small = ImageSpecField([ResizeToFill(48, 48)], image_field='imagefile_original', format='PNG')
    EVENT_TYPES = (
        (0, u'Kompo'),
        (1, u'Kilpailu'),
        (2, u'Ohjelmatapahtuma')
    )
    type = models.IntegerField(u'Tyyppi', help_text=u'Tapahtuman tyyppi', choices=EVENT_TYPES, default=0)
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name=u"kalenteritapahtuma"
        verbose_name_plural=u"kalenteritapahtumat"
        
    
try:
    admin.site.register(CalendarEvent)
except:
    pass