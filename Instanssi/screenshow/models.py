# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from Instanssi.kompomaatti.models import Event

class Sponsor(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    name = models.CharField(u'Nimi', max_length=64, help_text=u'Sponsorin nimi')
    logo = models.ImageField(u'Kuva', upload_to='screen/sponsorlogos/', help_text=u"Sponsorin logo", blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name=u"sponsori"
        verbose_name_plural=u"sponsorit"

    def save(self, *args, **kwargs):
        try:
            this = Sponsor.objects.get(id=self.id)
            if this.logo != self.logo:
                this.logo.delete(save=False)
        except: 
            pass 
        
        # Continue with normal save
        super(Sponsor, self).save(*args, **kwargs)
            

class Message(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    show_start = models.DateTimeField(u'Alkuaika', help_text=u'Viestin näyttäminen alkaa')
    show_end = models.DateTimeField(u'Loppuaika', help_text=u'Viestin näyttäminen päättyy')
    text = models.TextField(u'Viesti', help_text=u'Viestin leipäteksti. Katso ettei tästä tule liian pitkä.')
    
    def __unicode__(self):
        return self.text[:16]+u' ...'
    
    class Meta:
        verbose_name=u"viesti"
        verbose_name_plural=u"viestit"
    
class IRCMessage(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    date = models.DateTimeField(u'Aika')
    nick = models.CharField(u'Nimimerkki', max_length=64)
    message = models.TextField(u'Viesti')
    
    def __unicode__(self):
        return self.message[:16]+u' ...'
    
    class Meta:
        verbose_name=u"irc-viesti"
        verbose_name_plural=u"irc-viestit"

# Register to admin-panel
try:
    admin.site.register(IRCMessage)
    admin.site.register(Message)
    admin.site.register(Sponsor)
except:
    pass