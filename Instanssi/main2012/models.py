# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin

class BlogEntry(models.Model):
    title = models.TextField(u'Otsikko')
    summary = models.TextField(u'Teksti')
    date = models.DateTimeField(u'Päivitetty')
    link = models.URLField(u'Linkki')
    name = models.CharField(u'Nimi', max_length=64)
    locked = models.BooleanField(u'Lukittu', help_text=u"Tätä entryä ei poisteta tai päivitetä automaattisesti RSS-feedistä.", default=False)
        
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name=u"blogientry"
        verbose_name_plural=u"blogientryt"
        
admin.site.register(BlogEntry)