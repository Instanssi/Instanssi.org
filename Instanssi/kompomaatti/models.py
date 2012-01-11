# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from imagekit.models import ImageSpec
from imagekit.processors import resize
from imagekit.admin import AdminThumbnail

class Compo(models.Model):
    name = models.CharField('Nimi', max_length=32)
    description = models.TextField('Kuvaus')
    adding_end = models.DateTimeField('Deadline entryjen lisäyksille')
    editing_end = models.DateTimeField('Deadline entryjen muokkauksille')
    compo_start = models.DateTimeField('Kompon aloitusaika')
    voting_start = models.DateTimeField('Äänestyksen alkamisaika')
    voting_end = models.DateTimeField('Äänestyksen päättymisaika')
    sizelimit = models.IntegerField('Kokoraja tiedostoille')
    active = models.BooleanField('Aktiivinen')
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name="kompo"
        verbose_name_plural="kompot"
    
class Entry(models.Model):
    user = models.ForeignKey(User, verbose_name="käyttäjä")
    compo = models.ForeignKey(Compo, verbose_name="kompo", help_text="Kompo johon osallistutaan")
    name = models.CharField('Nimi', max_length=64, help_text='Nimi tuotokselle')
    description = models.TextField('Kuvaus', help_text='Voi sisältää mm. tietoja käytetyistä tekniikoista, muuta sanottavaa.')
    creator = models.CharField('Tekijä', max_length=64, help_text='Tuotoksen tekijän tai tekijäryhmän nimi')
    entryfile = models.FileField('Tiedosto', upload_to='entries/', help_text="Tuotospaketti. Esim. mp3, ogg, zip, jne. kelpaavat.")
    imagefile_original = models.ImageField('Kuva', upload_to='entryimages/', help_text="Edustava kuva teokselle. Ei pakollinen, mutta suositeltava.", blank=True)
    imagefile_thumbnail = ImageSpec([resize.Fit(320, 240)], image_field='imagefile_original', format='JPEG', options={'quality': 90})
    def __unicode__(self):
        return self.name + ' by ' + self.creator + ' (uploaded by ' + self.user.username + ')'
    class Meta:
        verbose_name="tuotos"
        verbose_name_plural="tuotokset"

class EntryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'admin_thumbnail')
    admin_thumbnail = AdminThumbnail(image_field='imagefile_thumbnail')

class Vote(models.Model):
    user = models.ForeignKey(User, verbose_name="käyttäjä")
    compo = models.ForeignKey(Compo, verbose_name="kompo")
    entry = models.ForeignKey(Entry, verbose_name="tuotos")
    rank = models.IntegerField('Sijoitus')
    def __unicode__(self):
        return self.entry.name + ' by ' + self.user.username + ' as ' + self.rank
    class Meta:
        verbose_name="ääni"
        verbose_name_plural="äänet"
    
admin.site.register(Compo)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Vote)