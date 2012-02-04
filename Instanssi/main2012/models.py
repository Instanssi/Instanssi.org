# -*- coding: utf-8 -*-

from django.db import models

class BlogEntry(models.Model):
    title = models.TextField(u'Otsikko')
    summary = models.TextField(u'Teksti')
    date = models.DateTimeField(u'Päivitetty')
    link = models.URLField(u'Linkki')
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name=u"blogientry"
        verbose_name_plural=u"blogientryt"