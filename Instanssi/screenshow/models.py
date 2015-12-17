# -*- coding: utf-8 -*-

from django.db import models
from Instanssi.kompomaatti.models import Event
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


class NPSong(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    title = models.CharField(u'Kappale', max_length=255, blank=True)
    artist = models.CharField(u'Artisti', max_length=255, blank=True)
    time = models.DateTimeField(u'Aikaleima')
    state = models.IntegerField(u'Tila', choices=((0, u'Play'), (1, u'Stop')))
    
    def __unicode__(self):
        if self.state == 0:
            return u'[Play] {} - {}'.format(self.title, self.artist)
        else:
            return u'[Stop]'
    
    class Meta:
        verbose_name = u"soitettava kappale"
        verbose_name_plural = u"soitettavat kappaleet"


class ScreenConfig(models.Model):
    event = models.OneToOneField(Event, verbose_name=u'Tapahtuma', unique=True)
    enable_videos = models.BooleanField(u'Näytä videoita', help_text=u'Näytetäänkö esityksessä videoita playlistiltä.', default=True)
    enable_twitter = models.BooleanField(u'Näytä twitterfeed', help_text=u'Näytetäänkö esityksessä twittersyötteen sisältävä slaidi.', default=True)
    enable_irc = models.BooleanField(u'Näytä IRC', help_text=u'Näytetäänkö esityksessä irc-lokin sisältävä slaidi.', default=True)
    video_interval = models.IntegerField(u'Videoiden näyttöväli', help_text=u'Kuinka usein videoita näytetään? Arvo annetaan minuuteissa. 0 = Joka kierroksella.', default=5)
    
    def __unicode__(self):
        return u'Asetukset tapahtumalle {}'.format(self.event.name)
    
    class Meta:
        verbose_name = u"screenikonffi"
        verbose_name_plural = u"screenikonffit"


class PlaylistVideo(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    name = models.CharField(u'Nimi', max_length=64, help_text=u'Videon nimi tai otsikko.')
    url = models.URLField(u'Osoite', help_text=u'Linkki Youtube-videoon.')
    index = models.IntegerField(u'Järjestysindeksi', help_text=u'Indeksi toistolistan järjestelemiseen. Pienimmällä '
                                                              u'numerolla varustetut toistetaan ensimmäiseksi.')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"toistolistavideo"
        verbose_name_plural = u"toistolistavideot"


class Sponsor(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    name = models.CharField(u'Nimi', max_length=64, help_text=u'Sponsorin nimi')
    logo = models.ImageField(u'Kuva', upload_to='screen/sponsorlogos/', help_text=u"Sponsorin logo", blank=True)
    logo_scaled = ImageSpecField([ResizeToFit(800, 375, True)], source='logo', format='PNG')

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = u"sponsori"
        verbose_name_plural = u"sponsorit"

    def save(self, *args, **kwargs):
        try:
            this = Sponsor.objects.get(id=self.id)
            if this.logo != self.logo:
                this.logo.delete(save=False)
        except Sponsor.DoesNotExist:
            pass 
        
        # Continue with normal save
        super(Sponsor, self).save(*args, **kwargs)
            

class Message(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    show_start = models.DateTimeField(u'Alkuaika', help_text=u'Viestin näyttäminen alkaa')
    show_end = models.DateTimeField(u'Loppuaika', help_text=u'Viestin näyttäminen päättyy')
    text = models.TextField(u'Viesti', help_text=u'Viestin leipäteksti. Katso ettei tästä tule liian pitkä.')
    
    def __unicode__(self):
        if len(self.text) > 32:
            return u'{} ...'.format(self.text[:32])
        else:
            return self.text
    
    class Meta:
        verbose_name = u"viesti"
        verbose_name_plural = u"viestit"


class IRCMessage(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    date = models.DateTimeField(u'Aika')
    nick = models.CharField(u'Nimimerkki', max_length=64)
    message = models.TextField(u'Viesti')
    
    def __unicode__(self):
        if len(self.message) > 32:
            return u'{} ...'.format(self.message[:32])
        else:
            return self.message
    
    class Meta:
        verbose_name = u"irc-viesti"
        verbose_name_plural = u"irc-viestit"
