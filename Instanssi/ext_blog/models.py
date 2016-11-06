# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from Instanssi.kompomaatti.models import Event


class BlogEntry(models.Model):
    event = models.ForeignKey(Event, verbose_name='Tapahtuma')
    user = models.ForeignKey(User, verbose_name='Käyttäjä')
    title = models.CharField('Otsikko', help_text='Lyhyt otsikko entrylle.', max_length=128)
    text = models.TextField('Teksti')
    date = models.DateTimeField('Aika')
    public = models.BooleanField(
        'Julkinen',
        help_text='Mikäli entry on julkinen, tulee se näkyviin sekä tapahtuman sivuille että RSS-syötteeseen.',
        default=False)

    def __unicode__(self):
        return '{} by {}'.format(self.title, self.user.username)

    class Meta:
        verbose_name = "entry"
        verbose_name_plural = "entryt"


class BlogComment(models.Model):
    user = models.ForeignKey(User, verbose_name='Käyttäjä')
    entry = models.ForeignKey(BlogEntry, verbose_name='Entry')
    title = models.CharField('Otsikko', help_text='Lyhyt otsikko kommentille.', max_length=128, blank=True)
    text = models.TextField('Kommentti', help_text='Kommenttiteksti.')
    date = models.DateTimeField('Aika')

    def __unicode__(self):
        return '{} by {}'.format(self.entry.title, self.user.username)

    class Meta:
        verbose_name = "kommentti"
        verbose_name_plural = "kommentit"
