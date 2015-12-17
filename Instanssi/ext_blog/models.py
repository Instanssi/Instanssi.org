# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from Instanssi.kompomaatti.models import Event


class BlogEntry(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    user = models.ForeignKey(User, verbose_name=u'Käyttäjä')
    title = models.CharField(u'Otsikko', help_text=u'Lyhyt otsikko entrylle.', max_length=128)
    text = models.TextField(u'Teksti')
    date = models.DateTimeField(u'Aika')
    public = models.BooleanField(
        u'Julkinen',
        help_text=u'Mikäli entry on julkinen, tulee se näkyviin sekä tapahtuman sivuille että RSS-syötteeseen.',
        default=False)

    def __unicode__(self):
        return u'{} by {}'.format(self.title, self.user.username)

    class Meta:
        verbose_name = u"entry"
        verbose_name_plural = u"entryt"


class BlogComment(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Käyttäjä')
    entry = models.ForeignKey(BlogEntry, verbose_name=u'Entry')
    title = models.CharField(u'Otsikko', help_text=u'Lyhyt otsikko kommentille.', max_length=128, blank=True)
    text = models.TextField(u'Kommentti', help_text=u'Kommenttiteksti.')
    date = models.DateTimeField(u'Aika')

    def __unicode__(self):
        return u'{} by {}'.format(self.entry.title, self.user.username)

    class Meta:
        verbose_name = u"kommentti"
        verbose_name_plural = u"kommentit"
