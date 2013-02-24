# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from Instanssi.kompomaatti.models import Event

class ProgrammeEvent(models.Model):
    event = models.ForeignKey(Event, verbose_name=u'Tapahtuma')
    start = models.DateTimeField(u'Alku', help_text=u'Tapahtuman alkamisaika.')
    end = models.DateTimeField(u'Loppu', help_text=u'Tapahtuman loppumisaika.', null=True, blank=True)
    description = models.TextField(u'Kuvaus', blank=True)
    title = models.CharField(u'Otsikko', help_text=u'Lyhyt otsikko.', max_length=128)
    presenters = models.CharField(u'Henkilöt', help_text=u'Esityksen pitäjät tms.', max_length=256, blank=True)
    presenters_titles = models.CharField(u'Nimikkeet', help_text=u'Henkilön arvo-, ammatti- tai virkanimike.', max_length=256, blank=True)
    
    # This is suck a hackish solution that it makes me want to throw up. Oh well.
    icon_original = models.ImageField(u'Kuva 1', upload_to='programme/images/', help_text=u"Kuva 1 tapahtumalle.", blank=True)
    icon_small = ImageSpecField([ResizeToFill(64, 64)], image_field='icon_original', format='PNG')
    icon2_original = models.ImageField(u'Kuva 2', upload_to='programme/images/', help_text=u"Kuva 2 tapahtumalle.", blank=True)
    icon2_small = ImageSpecField([ResizeToFill(64, 64)], image_field='icon2_original', format='PNG')
    
    email = models.EmailField(u'Sähköposti', help_text=u'Tapahtumaan liittyvä sähköposti-osoite (esim. esiintyjän).', blank=True)
    home_url = models.URLField(u'Kotiurli', help_text=u'Tapahtumaan liittyvä URL.', blank=True)
    twitter_url = models.URLField(u'Twitter', help_text=u'Tapahtumaan liittyvä Twitter-url.', blank=True)
    github_url = models.URLField(u'Github', help_text=u'Tapahtumaan liittyvä Github-url', blank=True)
    facebook_url = models.URLField(u'Facebook', help_text=u'Tapahtumaan liittyvä facebook-url.', blank=True)
    linkedin_url = models.URLField(u'LinkedIn', help_text=u'Tapahtumaan liittyvä LinkedIn-url.', blank=True)
    wiki_url = models.URLField(u'Wikipedia', help_text=u'Tapahtumaan liittyvä Wikipedia-url.', blank=True)
    gplus_url = models.URLField(u'Google+', help_text=u'Tapahtumaan liittyvä Google Plus-url.', blank=True)
    EVENT_TYPES = (
        (0, u'Yksinkertainen'),
        (1, u'Yksityiskohtainen'),
    )
    event_type = models.IntegerField(u'Tapahtuman tyyppi', choices=EVENT_TYPES, default=0, help_text=u"Määrittää tapahtuman tyypin. Yksityiskohtaiset tapahtumat näkyvät etusivun tapahtumalistassa.")
    active = models.BooleanField(u'Aktiivinen', help_text=u'Deaktivoidut piilotetaan.', default=True)

    def save(self, *args, **kwargs):
        # Delete old icon file when editing
        try:
            this = ProgrammeEvent.objects.get(id=self.id)
            if this.icon_original != self.icon_original:
                this.icon_original.delete(save=False)
        except: 
            pass 
            
        # Continue with normal save
        super(ProgrammeEvent, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name=u"ohjelmatapahtuma"
        verbose_name_plural=u"ohjelmatapahtumat"

try:
    admin.site.register(ProgrammeEvent)
except:
    pass