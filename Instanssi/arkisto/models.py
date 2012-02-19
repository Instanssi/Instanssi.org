# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin

class Tag(models.Model):
    name = models.CharField('Tag', max_length=32)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name=u"tagi"
        verbose_name_plural=u"tagit"

class Event(models.Model):
    name = models.CharField('Nimi', max_length=32)
    date = models.DateField('Päivämäärä')
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name=u"tapahtuma"
        verbose_name_plural=u"tapahtumat"
    
class Compo(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField('Nimi', max_length=32)
    description = models.TextField('Kuvaus')
    def __unicode__(self):
        return self.event.name + ": " + self.name
    class Meta:
        verbose_name=u"kompo"
        verbose_name_plural=u"kompot"

class Entry(models.Model):
    compo = models.ForeignKey(Compo)
    name = models.CharField('Nimi', max_length=32)
    description = models.TextField('Kuvaus')
    creator = models.CharField('Tekijä', max_length=64)
    file = models.FileField('Tiedosto', upload_to='arkisto/entryfiles/')
    imagefile_original = models.ImageField(u'Kuva', upload_to='arkisto/entryimages/', blank=True)
    imagefile_small = ImageSpec([resize.Fit(160, 100)], image_field='imagefile_original', format='JPEG', options={'quality': 90})
    imagefile_medium = ImageSpec([resize.Fit(640, 420)], image_field='imagefile_original', format='JPEG', options={'quality': 90})
    youtube_url = models.URLField('Youtube URL', blank=True)
    tags = models.ManyToManyField(Tag)
    position = models.IntegerField('Sijoitus')
    def __unicode__(self):
        return self.compo.name + " " + self.name
    class Meta:
        verbose_name=u"tuotos"
        verbose_name_plural=u"tuotokset"

# Register models to admin panel
try:
    admin.site.register(Tag)
except:
    pass
try:
    admin.site.register(Event)
except:
    pass
try:
    admin.site.register(Compo)
except:
    pass
try:
    admin.site.register(Entry)
except:
    pass
