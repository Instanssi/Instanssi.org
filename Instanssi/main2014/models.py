# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class ToimistoJahti(models.Model):
    key = models.CharField(
        'Avain', max_length=10, help_text="Avain", unique=True)
    help = models.TextField(
        'Ohje', help_text='Ohjeteksti')
    
    def __str__(self):
        if len(self.help) > 15:
            return self.key + ': ' + self.help[:15] + ' ...'
        else:
            return self.key + ': ' + self.help
        
    class Meta:
        verbose_name = "jahtitehtava"
        verbose_name_plural = "jahtitehtavat"


class ToimistoSuoritus(models.Model):
    user = models.ForeignKey(
        User, verbose_name='Käyttäjä', on_delete=models.CASCADE)
    nick = models.CharField(
        'Tunnusnimi', max_length=32, help_text="Agentin tunnusnimi", unique=True)
    time = models.DateTimeField(
        'Suoritusaika', help_text="Aika, jolloin agentti merkkasi tehtävän suoritetuksi")
    
    def __str__(self):
        return self.nick
    
    class Meta:
        verbose_name = "toimistosuoritus"
        verbose_name_plural = "toimistosuoritukset"
