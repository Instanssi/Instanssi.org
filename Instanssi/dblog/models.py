# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from Instanssi.kompomaatti.models import Event


class DBLogEntry(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    event = models.ForeignKey(Event, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    module = models.CharField(max_length=64, blank=True)
    level = models.CharField(max_length=10)
    message = models.TextField()

    def __unicode__(self):
        if len(self.message) > 48:
            return u' ...'.format(self.message[:48])
        else:
            return self.message
    
    class Meta:
        verbose_name = u"lokimerkintä"
        verbose_name_plural = u"lokimerkinnät"
