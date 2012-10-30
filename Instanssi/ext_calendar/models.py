# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from Instanssi.kompomaatti.models import Event, Compo
from Instanssi.ext_programme.models import ProgrammeEvent

class CalendarEvent(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    start = models.DateTimeField(u'Alku', help_text=u'Tapahtuman alkamisaika.')
    end = models.DateTimeField(u'Loppu', help_text=u'Tapahtuman loppumisaika.', null=True, blank=True)
    description = models.TextField(u'Kuvaus', help_text=u'Tapahtuman kuvaus.', blank=True)
    title = models.CharField(u'Otsikko', help_text=u'Lyhyt otsikko.', max_length=64)
    icon_original = models.ImageField(u'Kuva', upload_to='calendar/images/', help_text=u"Kuva tapahtumalle.", blank=True)
    icon_small = ImageSpecField([ResizeToFill(64, 64)], image_field='icon_original', format='PNG')
    
    def save(self, *args, **kwargs):
        # Delete old icon file when editing
        try:
            this = CalendarEvent.objects.get(id=self.id)
            if this.icon_original != self.icon_original:
                this.icon_original.delete(save=False)
        except: 
            pass 
            
        # Continue with normal save
        super(CalendarEvent, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name=u"kalenteritapahtuma"
        verbose_name_plural=u"kalenteritapahtumat"
        
try:
    admin.site.register(CalendarEvent)
except:
    pass