# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from Instanssi.kompomaatti.models import Event
import os.path


class UploadedFile(models.Model):
    event = models.ForeignKey(Event, verbose_name='Tapahtuma')
    user = models.ForeignKey(User, verbose_name='Käyttäjä')
    description = models.TextField(
        'Kuvaus', help_text='Lyhyt kuvaus siitä, mihin/missä tiedostoa käytetään.', blank=True)
    file = models.FileField('Tiedosto', upload_to='files/')
    date = models.DateTimeField('Aika')
    
    def __unicode__(self):
        return '{} by {}'.format(self.file.name, self.user.username)
    
    class Meta:
        verbose_name = "tiedosto"
        verbose_name_plural = "tiedostot"
        
    def name(self):
        return os.path.basename(self.file.name)
        
    def save(self, *args, **kwargs):
        # Delete old file when editing
        try:
            this = UploadedFile.objects.get(id=self.id)
            if this.file != self.file:
                this.file.delete(save=False)
        except UploadedFile.DoesNotExist:
            pass 
            
        # Continue with normal save
        super(UploadedFile, self).save(*args, **kwargs)
