# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from Instanssi.kompomaatti.models import Event

class ProgrammeEvent(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    description = models.TextField(u'Kuvaus', help_text=u'Tapahtuman kuvaus.')
    title = models.CharField(u'Otsikko', help_text=u'Lyhyt otsikko.', max_length=64)
    presenters = models.CharField(u'Henkilöt', help_text=u'Esityksen pitäjät tms.', max_length=256)
    presenters_titles = models.CharField(u'Nimitykset', help_text=u'Pitäjien nimitykset (Konsultti, jne.)', max_length=256)
    icon_original = models.ImageField(u'Kuva', upload_to='programme/images/', help_text=u"Kuva tapahtumalle.", blank=True)
    icon_small = ImageSpecField([ResizeToFill(64, 64)], image_field='imagefile_original', format='PNG')
    email = models.EmailField(u'Sähköposti', help_text=u'Tapahtumaan liittyvä sähköposti-osoite (esim. esiintyjän).', blank=True)
    home_url = models.URLField(u'Kotiurli', help_text=u'Tapahtumaan liittyvä URL.', blank=True)
    twitter_url = models.URLField(u'Twitter', help_text=u'Tapahtumaan liittyvä Twitter-url.', blank=True)
    facebook_url = models.URLField(u'Facebook', help_text=u'Tapahtumaan liittyvä facebook-url.', blank=True)
    linkedin_url = models.URLField(u'LinkedIn', help_text=u'Tapahtumaan liittyvä LinkedIn-url.', blank=True)
    wiki_url = models.URLField(u'Wikipedia', help_text=u'Tapahtumaan liittyvä Wikipedia-url.', blank=True)

    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name=u"ohjelmatapahtuma"
        verbose_name_plural=u"ohjelmatapahtumat"

try:
    admin.site.register(ProgrammeEvent)
except:
    pass