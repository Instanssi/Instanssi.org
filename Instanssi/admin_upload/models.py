# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from Instanssi.kompomaatti.models import Event
import os.path

class UploadedFile(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    user = models.ForeignKey(User, verbose_name=u'Käyttäjä')
    description = models.TextField(u'Kuvaus', help_text=u'Lyhyt kuvaus siitä, mihin/missä tiedostoa käytetään.', blank=True)
    file = models.FileField(u'Tiedosto', upload_to='files/')
    date = models.DateTimeField(u'Aika')
    
    def __unicode__(self):
        return self.file.name + ' by ' + self.user.username
    
    class Meta:
        verbose_name=u"tiedosto"
        verbose_name_plural=u"tiedostot"
        
    def name(self):
        return os.path.basename(self.file.name)

try:
    admin.site.register(UploadedFile)
except:
    pass