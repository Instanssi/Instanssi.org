# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

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
    
class Entry(models.Model):
    user = models.ForeignKey(User)
    compo = models.ForeignKey(Compo)
    name = models.CharField('nimi', max_length=64)
    description = models.TextField('Kuvaus')
    creator = models.CharField('Tekijä', max_length=64)
    entryfile = models.FileField(upload_to='entries/')
    def __unicode__(self):
        return self.name + ' by ' + self.creator + ' (uploaded by ' + self.user.username + ')'

class Vote(models.Model):
    user = models.ForeignKey(User)
    compo = models.ForeignKey(Compo)
    entry = models.ForeignKey(Entry)
    rank = models.IntegerField('Sijoitus')
    def __unicode__(self):
        return self.entry.name + ' by ' + self.user.username + ' as ' + self.rank
    
admin.site.register(Compo)
admin.site.register(Entry)
admin.site.register(Vote)