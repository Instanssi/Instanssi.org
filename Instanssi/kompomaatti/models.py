# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from imagekit.models import ImageSpec
from imagekit.processors import resize
from imagekit.admin import AdminThumbnail
from datetime import datetime
import os.path

class VoteCodeRequest(models.Model):
    user = models.ForeignKey(User, unique=True, verbose_name=u'Käyttäjä', help_text=u'Pyynnön esittänyt käyttäjä')
    text = models.TextField(u'Kuvaus', help_text=u'Lyhyt aneluteksti admineille :)')
    
    def __unicode__(self):
        return self.user.username
    
    class Meta:
        verbose_name=u"äänestyskoodipyyntö"
        verbose_name_plural=u"äänestyskoodipyynnöt"

class VoteCode(models.Model):
    key = models.CharField(u'Avain', help_text=u"Äänestysavain.", max_length=64, unique=True)
    associated_to = models.ForeignKey(User, unique=True, verbose_name=u'Käyttäjä', help_text=u"Käyttäjä jolle avain on assosioitu", blank=True, null=True)
    time = models.DateTimeField(u'Aikaleima', help_text=u"Aika jolloin avain assosioitiin käyttäjälle.", blank=True, null=True)

    def __unicode__(self):
        return self.key
    
    class Meta:
        verbose_name=u"äänestysavain"
        verbose_name_plural=u"äänestysavaimet"

class Compo(models.Model):
    name = models.CharField(u'Nimi', max_length=32, help_text=u"Kompon nimi (max 32 merkkiä).")
    description = models.TextField(u'Kuvaus', help_text=u"Kuvaus kompolle; esim. vaatimukset, esimerkit, jne.")
    adding_end = models.DateTimeField(u'Deadline entryjen lisäyksille', help_text=u"Tämän jälkeen kompoon ei voi enää lähettää uusia entryjä. Muokkaus toimii vielä.")
    editing_end = models.DateTimeField(u'Deadline entryjen muokkauksille', help_text=u"Tämän jälkeen entryjen tiedostoja tai muita tietoja ei voi enää muokata.")
    compo_start = models.DateTimeField(u'Kompon aloitusaika', help_text=u"Kompon alkamisaika tapahtumassa (tapahtumakalenteria varten).")
    voting_start = models.DateTimeField(u'Äänestyksen alkamisaika', help_text=u"Alkamisaika entryjen äänestykselle.")
    voting_end = models.DateTimeField(u'Äänestyksen päättymisaika', help_text=u'Päättymisaika entryjen äänestykselle.')
    entry_sizelimit = models.IntegerField(u'Kokoraja entryille', help_text=u"Kokoraja entrytiedostoille (tavua).", default=134217728) # Default to 128M
    source_sizelimit = models.IntegerField(u'Kokoraja sorsille', help_text=u"Kokoraja sorsatiedostoille (tavua).", default=134217728) # Default to 128M
    formats = models.CharField(u'Sallitut tiedostopäätteet', max_length=128, help_text=u"Entrypaketille sallitut tiedostopäätteet pystyviivalla eroteltuna, esim. \"png|jpg|gif\".", default="zip|7z|gz|bz2")
    source_formats = models.CharField(u'Sallitut lähdekoodipaketin päätteet', max_length=128, help_text=u"Entryn lähdekoodipaketille sallitut tiedostopäätteet pystyviivalla eroteltuna", default="zip|7z|gz|bz2")
    active = models.BooleanField(u'Aktiivinen', help_text=u"Onko kompo aktiivinen, eli näytetäänkö se kompomaatissa kaikille.", default=True)
    show_voting_results = models.BooleanField(u'Näytä tulokset', help_text=u"Näytä äänestustulokset.", default=False)
    ENTRY_VIEW_TYPES = (
        (0, u'Ei mitään'),
        (1, u'Youtube ensin, sitten kuva'), # Videoentryille, koodauskompoille
        (2, u'Vain kuva'), # Grafiikkakompoille
        (3, u'jPlayer ensin, sitten kuva'), # Musiikkikompoille
    )
    entry_view_type = models.IntegerField(u'Entryesittely', choices=ENTRY_VIEW_TYPES, default=0, help_text=u"Millainen näkymä näytetään entryn tiedoissa? Prioriteetti ja tyyppi. Latauslinkki näytetään aina.")
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name=u"kompo"
        verbose_name_plural=u"kompot"
            
    def readable_entry_formats(self):
        return ', '.join(self.formats.split('|'))
    
    def readable_source_formats(self):
        return ', '.join(self.source_formats.split('|'))

class Entry(models.Model):
    user = models.ForeignKey(User, verbose_name="käyttäjä", help_text=u"Käyttäjä jolle entry kuuluu")
    compo = models.ForeignKey(Compo, verbose_name="kompo", help_text=u"Kompo johon osallistutaan")
    name = models.CharField(u'Nimi', max_length=64, help_text=u'Nimi tuotokselle')
    description = models.TextField(u'Kuvaus', help_text=u'Voi sisältää mm. tietoja käytetyistä tekniikoista, muuta sanottavaa.')
    creator = models.CharField(u'Tekijä', max_length=64, help_text=u'Tuotoksen tekijän tai tekijäryhmän nimi')
    entryfile = models.FileField(u'Tiedosto', upload_to='entries/', help_text=u"Tuotospaketti.")
    sourcefile = models.FileField(u'Lähdekoodi', upload_to='entrysources/', help_text=u"Lähdekoodipaketti.", blank=True)
    imagefile_original = models.ImageField(u'Kuva', upload_to='entryimages/', help_text=u"Edustava kuva teokselle. Ei pakollinen, mutta suositeltava.", blank=True)
    imagefile_thumbnail = ImageSpec([resize.Fit(320, 240)], image_field='imagefile_original', format='JPEG', options={'quality': 90})
    youtube_url = models.URLField(u'Youtube URL', help_text=u"Linkki teoksen Youtube-versioon. Täytyy olla muotoa \"http://www.youtube.com/v/abcabcabcabc\".", blank=True)
    disqualified = models.BooleanField(u'Diskattu', help_text=u"Entry on diskattu sääntörikon tai teknisten ongelmien takia. DISKAUS ON TEHTÄVÄ ENNEN ÄÄNESTYKSEN ALKUA!", default=False)
    disqualified_reason = models.TextField(u'Syy diskaukseen', help_text=u"Diskauksen syy.", blank=True)
    
    def __unicode__(self):
        return self.name + ' by ' + self.creator + ' (uploaded by ' + self.user.username + ')'
    
    class Meta:
        verbose_name=u"tuotos"
        verbose_name_plural=u"tuotokset"
        
    def get_entry_jplayer_ext(self):
        ext = os.path.splitext(self.entryfile.name)[1][1:]
        if ext == 'ogg':
            ext = 'oga'
        if ext == 'ogm':
            ext = 'ogv'
        return ext
    
    def can_use_jplayer(self):
        ext = os.path.splitext(self.entryfile.name)[1][1:]
        return (ext in ['mp3','oga','ogv'])
    
class Vote(models.Model):
    user = models.ForeignKey(User, verbose_name=u"käyttäjä")
    compo = models.ForeignKey(Compo, verbose_name=u"kompo")
    entry = models.ForeignKey(Entry, verbose_name=u"tuotos")
    rank = models.IntegerField(u'Sijoitus')
    
    def __unicode__(self):
        return self.entry.name + ' by ' + self.user.username + ' as ' + str(self.rank)
    
    class Meta:
        verbose_name=u"ääni"
        verbose_name_plural=u"äänet"


admin.site.register(Compo)
admin.site.register(Entry)
admin.site.register(Vote)
admin.site.register(VoteCode)