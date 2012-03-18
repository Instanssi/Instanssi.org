# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from imagekit.models import ImageSpec
from imagekit.processors import resize

class CalendarEvent(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Käyttäjä')
    start = models.DateTimeField(u'Alku', help_text=u'Tapahtuman alkamisaika.')
    end = models.DateTimeField(u'Loppe', help_text=u'Tapahtuman loppumisaika.', blank=True)
    description = models.TextField(u'Kuvaus', help_text=u'Tapahtuman kuvaus.', blank=True)
    title = models.CharField(u'Otsikko', help_text=u'Lyhyt otsikko.', max_length=32)
    image_original = models.ImageField(u'Kuva', upload_to='calendar/images/', help_text=u"Kuva tapahtumalle.", blank=True)
    image_small = ImageSpec([resize.Fit(48, 48)], image_field='imagefile_original', format='PNG')
    EVENT_TYPES = (
        (0, u'Aikaraja'),
        (1, u'Aikavaraus'),
    )
    type = models.IntegerField(u'Tyyppi', help_text=u'Tapahtuman tyyppi', choices=EVENT_TYPES, default=0)
    
try:
    admin.site.register(CalendarEvent)
except:
    pass