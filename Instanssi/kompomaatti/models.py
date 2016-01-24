# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from datetime import datetime
from urlparse import urlparse
from Instanssi.kompomaatti.misc import entrysort
from Instanssi.store.models import TransactionItem
import os.path


class Profile(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=u'Käyttäjä')
    otherinfo = models.TextField(
        u'Muut yhteystiedot',
        help_text=u'Muita yhteystietoja, mm. IRC-tunnus (verkon kera), jne.')

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = u"profiili"
        verbose_name_plural = u"profiilit"


class Event(models.Model):
    name = models.CharField(
        u'Nimi',
        max_length=64,
        help_text=u"Tapahtuman nimi",
        unique=True)
    date = models.DateField(
        u'Päivämäärä',
        help_text=u"Tapahtuman päivämäärä (alku)")
    archived = models.BooleanField(
        u'Arkistoitu',
        help_text=u"Saa näyttää arkistossa",
        default=False)
    mainurl = models.URLField(
        u'Tapahtuman pääsivu', help_text=u'URL Tapahtuman pääsivustolle', blank=True)

    def __unicode__(self):
        return u'[{}] {}'.format(self.pk, self.name)

    class Meta:
        verbose_name = u"tapahtuma"
        verbose_name_plural = u"tapahtumat"


class VoteCodeRequest(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=u'Tapahtuma',
        help_text=u'Tapahtuma, johon äänestysoikeutta pyydetään',
        null=True)
    user = models.OneToOneField(
        User,
        unique=True,
        verbose_name=u'Käyttäjä',
        help_text=u'Pyynnön esittänyt käyttäjä')
    text = models.TextField(
        u'Kuvaus',
        help_text=u'Lyhyt aneluteksti admineille :)')

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = u"äänestyskoodipyyntö"
        verbose_name_plural = u"äänestyskoodipyynnöt"


class TicketVoteCode(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=u'Tapahtuma',
        help_text=u'Tapahtuma, johon äänestysavain on assosioitu',
        blank=True,
        null=True)
    associated_to = models.ForeignKey(
        User,
        verbose_name=u'Käyttäjä',
        help_text=u"Käyttäjä jolle avain on assosioitu",
        blank=True,
        null=True)
    ticket = models.ForeignKey(
        TransactionItem,
        verbose_name=u'Lipputuote',
        help_text=u'Lipputuote jonka avainta käytetään äänestysavaimena',
        blank=True,
        null=True)
    time = models.DateTimeField(
        u'Aikaleima',
        help_text=u"Aika jolloin avain assosioitiin käyttäjälle.",
        blank=True,
        null=True)

    def __unicode__(self):
        return u'{}: {}'.format(self.ticket.key, self.associated_to.username)

    class Meta:
        verbose_name = u"lippuäänestusavain"
        verbose_name_plural = u"lippuäänestysavaimet"
        unique_together = (("event", "ticket"), ("event", "associated_to"))


class VoteCode(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name=u'Tapahtuma',
        help_text=u'Tapahtuma, johon äänestysavain on assosioitu',
        blank=True,
        null=True)
    key = models.CharField(
        u'Avain',
        help_text=u"Äänestysavain.",
        max_length=64,
        unique=True)
    associated_to = models.ForeignKey(
        User,
        verbose_name=u'Käyttäjä',
        help_text=u"Käyttäjä jolle avain on assosioitu",
        blank=True,
        null=True)
    time = models.DateTimeField(
        u'Aikaleima',
        help_text=u"Aika jolloin avain assosioitiin käyttäjälle.",
        blank=True,
        null=True)

    def __unicode__(self):
        if self.associated_to:
            return u'{}: {}'.format(self.key, self.associated_to.username)
        else:
            return unicode(self.key)

    class Meta:
        verbose_name = u"äänestysavain"
        verbose_name_plural = u"äänestysavaimet"
        unique_together = (("event", "key"), ("event", "associated_to"))


class Compo(models.Model):
    ENTRY_VIEW_TYPES = (
        (0, u'Ei mitään'),
        (1, u'Youtube ensin, sitten kuva'),  # Videoentryille, koodauskompoille
        (2, u'Vain kuva'),  # Grafiikkakompoille
        (3, u'(deprecated)'),
    )
    THUMBNAIL_REQ = (
        (0, u'Vaadi erillinen pikkukuva.'),
        (1, u'Käytä pikkukuvana teoksen tiedostoa (Toimii vain png/jpg-tiedostoille).'),
        (2, u'Salli pikkukuva (ei vaadittu).'),
        (3, u'Älä salli pikkukuvaa.'),
    )

    event = models.ForeignKey(
        Event,
        verbose_name=u"tapahtuma",
        help_text=u"Tapahtuma johon kompo kuuluu")
    name = models.CharField(
        u'Nimi',
        max_length=32,
        help_text=u"Kompon nimi (max 32 merkkiä).")
    description = models.TextField(
        u'Kuvaus')
    adding_end = models.DateTimeField(
        u'Deadline entryjen lisäyksille',
        help_text=u"Tämän jälkeen kompoon ei voi enää lähettää uusia entryjä. Muokkaus toimii vielä.")
    editing_end = models.DateTimeField(
        u'Deadline entryjen muokkauksille',
        help_text=u"Tämän jälkeen entryjen tiedostoja tai muita tietoja ei voi enää muokata.")
    compo_start = models.DateTimeField(
        u'Kompon aloitusaika',
        help_text=u"Kompon alkamisaika tapahtumassa (tapahtumakalenteria varten).")
    voting_start = models.DateTimeField(
        u'Äänestyksen alkamisaika',
        help_text=u"Alkamisaika entryjen äänestykselle.")
    voting_end = models.DateTimeField(
        u'Äänestyksen päättymisaika',
        help_text=u'Päättymisaika entryjen äänestykselle.')
    entry_sizelimit = models.IntegerField(
        u'Kokoraja entryille',
        help_text=u"Kokoraja entrytiedostoille (tavua).",
        default=134217728)  # Default to 128M
    source_sizelimit = models.IntegerField(
        u'Kokoraja sorsille',
        help_text=u"Kokoraja sorsatiedostoille (tavua).",
        default=134217728)  # Default to 128M
    formats = models.CharField(
        u'Sallitut tiedostopäätteet',
        max_length=128,
        help_text=u"Entrypaketille sallitut tiedostopäätteet pystyviivalla eroteltuna, esim. \"png|jpg\".",
        default="zip|7z|gz|bz2")
    source_formats = models.CharField(
        u'Sallitut lähdekoodipaketin päätteet',
        max_length=128,
        help_text=u"Entryn lähdekoodipaketille sallitut tiedostopäätteet pystyviivalla eroteltuna",
        default="zip|7z|gz|bz2")
    image_formats = models.CharField(
        u'Sallitut kuvatiedoston päätteet',
        max_length=128,
        help_text=u"Entryn pikkukuvalle sallitut tiedostopäätteet pystyviivalla eroteltuna",
        default="png|jpg")
    active = models.BooleanField(
        u'Aktiivinen',
        help_text=u"Onko kompo aktiivinen, eli näytetäänkö se kompomaatissa kaikille.",
        default=True)
    show_voting_results = models.BooleanField(
        u'Näytä tulokset',
        help_text=u"Näytä äänestustulokset.",
        default=False)
    entry_view_type = models.IntegerField(
        u'Entryesittely',
        choices=ENTRY_VIEW_TYPES,
        default=0,
        help_text=u"Ilmoittaa millainen näkymä näytetään entryn tiedoissa. Latauslinkki näytetään aina.")
    hide_from_archive = models.BooleanField(
        u'Piilotus arkistosta',
        help_text=u'Piilottaa kompon tulokset arkistosta. Tämä asetus ohittaa tapahtuman tiedoissa valitun asetuksen.',
        default=False)
    hide_from_frontpage = models.BooleanField(
        u'Piilotus etusivulta',
        help_text=u'Piilottaa kompon nimen ja kuvauksen tapahtuman etusivulta. '
                  u'Käytä esim. jos kompon kuvaus on vielä suunnitteilla.',
        default=False)
    is_votable = models.BooleanField(
        u'Äänestettävissä',
        help_text=u'Teosta voi ylipäätään äänestää (Pois esim. robocodelle).',
        default=True)
    thumbnail_pref = models.IntegerField(
        u'Pikkukuvan asetukset',
        choices=THUMBNAIL_REQ,
        default=2,
        help_text=u'Pikkukuvan luonti ja asettaminen.')
    
    def __unicode__(self):
        return self.event.name + ': ' + self.name
    
    class Meta:
        verbose_name = u"kompo"
        verbose_name_plural = u"kompot"
            
    def is_voting_open(self):
        if not self.is_votable:
            return False
        if self.voting_start <= datetime.now() < self.voting_end:
            return True
        return False
    
    def is_adding_open(self):
        if datetime.now() < self.adding_end:
            return True
        return False

    def is_editing_open(self):
        if datetime.now() < self.editing_end:
            return True
        return False

    def has_voting_started(self):
        if not self.is_votable:
            return False
        if datetime.now() > self.voting_start:
            return True
        return False

    def readable_entry_formats(self):
        return u', '.join(self.formats.split('|'))

    def readable_source_formats(self):
        return u', '.join(self.source_formats.split('|'))

    def readable_image_formats(self):
        return ', '.join(self.image_formats.split('|'))


class Entry(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=u"käyttäjä",
        help_text=u"Käyttäjä jolle entry kuuluu")
    compo = models.ForeignKey(
        Compo,
        verbose_name=u"kompo",
        help_text=u"Kompo johon osallistutaan")
    name = models.CharField(
        u'Nimi',
        max_length=64,
        help_text=u'Nimi tuotokselle')
    description = models.TextField(
        u'Kuvaus',
        help_text=u'Voi sisältää mm. tietoja käytetyistä tekniikoista, muuta sanottavaa.')
    creator = models.CharField(
        u'Tekijä',
        max_length=64,
        help_text=u'Tuotoksen tekijän tai tekijäryhmän nimi')
    entryfile = models.FileField(
        u'Tiedosto',
        upload_to='kompomaatti/entryfiles/',
        help_text=u"Tuotospaketti.")
    sourcefile = models.FileField(
        u'Lähdekoodi',
        upload_to='kompomaatti/entrysources/',
        help_text=u"Lähdekoodipaketti.",
        blank=True)
    imagefile_original = models.ImageField(
        u'Kuva',
        upload_to='kompomaatti/entryimages/',
        help_text=u"Edustava kuva teokselle. Ei pakollinen, mutta suositeltava.",
        blank=True)
    imagefile_thumbnail = ImageSpecField(
        [ResizeToFill(160, 100)],
        source='imagefile_original',
        format='JPEG',
        options={'quality': 90})
    imagefile_medium = ImageSpecField(
        [ResizeToFill(640, 400)],
        source='imagefile_original',
        format='JPEG',
        options={'quality': 90})
    youtube_url = models.URLField(
        u'Youtube URL',
        help_text=u"Linkki teoksen Youtube-videoon.",
        blank=True)
    disqualified = models.BooleanField(
        u'Diskattu',
        help_text=u"Entry on diskattu sääntörikon tai teknisten ongelmien takia. "
                  u"DISKAUS ON TEHTÄVÄ ENNEN ÄÄNESTYKSEN ALKUA!",
        default=False)
    disqualified_reason = models.TextField(
        u'Syy diskaukseen',
        help_text=u"Diskauksen syy.",
        blank=True)
    archive_score = models.FloatField(
        u'Pisteet',
        help_text=u'Arkistoidun entryn kompossa saamat pisteet. Mikäli tätä ei määritetä, '
                  u'lasketaan pisteet suoraan äänestystuloksista.',
        null=True,
        blank=True)
    archive_rank = models.IntegerField(
        u'Sijoitus',
        help_text=u'Arkistoidun entryn kompossa saama sijoitus. '
                  u'Tämä voidaan laskea myös pistemääristä automaattisesti.',
        null=True,
        blank=True)

    def __unicode__(self):
        return u'{} by {}'.format(self.name, self.creator)
    
    class Meta:
        verbose_name = u"tuotos"
        verbose_name_plural = u"tuotokset"
    
    def get_format(self):
        name, ext = os.path.splitext(self.entryfile.url)
        return ext
    
    def get_score(self):
        if self.disqualified:  # If disqualified, score will be -1
            return -1.0
        elif self.archive_score:  # If entry is archived, the score will be simple to get
            return self.archive_score
        else:  # Otherwise the score has to be calculated
            score = 0.0
            votes = Vote.objects.filter(entry=self, compo=self.compo)
            for vote in votes:
                if vote.rank > 0:
                    score += (1.0 / vote.rank)
            return score
        
    def get_youtube_embed_url(self):
        split_url = urlparse(self.youtube_url)
        return u"http://www.youtube.com/embed/{}/".format(os.path.split(split_url.path)[1])
        
    def get_rank(self):
        # If rank has been predefined, then use that
        if self.archive_rank:
            return self.archive_rank
        
        # Otherwise calculate ranks by score
        entries = entrysort.sort_by_score(Entry.objects.filter(compo=self.compo))
        n = 1
        for e in entries:
            if e.id == self.id:
                return n
            n += 1
        return n
    
    def get_show_list(self):
        show = {
            'youtube': False,
            'image': False,
            'noshow': True
        }
        
        state = self.compo.entry_view_type
        if state == 1:
            if self.youtube_url:
                show['youtube'] = True
            elif self.imagefile_original:
                show['image'] = True
        elif state == 2 or state == 3:  # 3 is deprecated
            if self.imagefile_original:
                show['image'] = True
        
        if show['image'] or show['youtube']:
            show['noshow'] = False
            
        return show
    
    def save(self, *args, **kwargs):
        try:
            this = Entry.objects.get(id=self.id)
            
            # Check entryfile
            if this.entryfile != self.entryfile:
                this.entryfile.delete(save=False)
                
            # Check sourcefile
            if this.sourcefile != self.sourcefile:
                this.sourcefile.delete(save=False)
                
            # Check imagefile_original
            if this.imagefile_original != self.imagefile_original:
                this.imagefile_original.delete(save=False)
        except:
            pass 
            
        # Continue with normal save
        super(Entry, self).save(*args, **kwargs)


class Vote(models.Model):
    user = models.ForeignKey(User, verbose_name=u"käyttäjä")
    compo = models.ForeignKey(Compo, verbose_name=u"kompo")
    entry = models.ForeignKey(Entry, verbose_name=u"tuotos")
    rank = models.IntegerField(u'Sijoitus')
    
    def __unicode__(self):
        return u'{} by {} as {}'.format(self.entry.name, self.user.username, self.rank)
    
    class Meta:
        verbose_name = u"ääni"
        verbose_name_plural = u"äänet"


class Competition(models.Model):
    ENTRY_VIEW_TYPES = (
        (0, u'Korkein tulos ensin'),
        (1, u'Matalin tulos ensin'),
    )

    event = models.ForeignKey(
        Event,
        verbose_name=u"Tapahtuma",
        help_text=u"Tapahtuma johon kilpailu kuuluu")
    name = models.CharField(
        u'Nimi',
        max_length=32,
        help_text=u"Kilpailun nimi (max 32 merkkiä).")
    description = models.TextField(
        u'Kuvaus')
    participation_end = models.DateTimeField(
        u'Deadline osallistumiselle.',
        help_text=u"Tämän jälkeen kilpailuun ei voi enää osallistua.")
    start = models.DateTimeField(
        u'Kilpailun alku',
        help_text=u"Kilpailun aloitusaika.")
    end = models.DateTimeField(
        u'Kilpailun loppu',
        help_text=u"Kilpailun päättymisaika.",
        null=True,
        blank=True)
    score_type = models.CharField(
        u'Pisteiden tyyppi',
        max_length=8,
        help_text=u'Pisteiden tyyppi (km, m, sek, ...). Maksimipituus 8 merkkiä.')
    score_sort = models.IntegerField(
        u'Pisteiden järjestely',
        choices=ENTRY_VIEW_TYPES,
        help_text=u'Onko suurimman vai pienimmän tuloksen saavuttanut voittaja?',
        default=0)
    show_results = models.BooleanField(
        u'Näytä tulokset',
        help_text=u"Näytä kilpailun tulokset.",
        default=False)
    active = models.BooleanField(
        u'Aktiivinen',
        help_text=u"Onko kilpailu aktiivinen, eli näytetäänkö se kompomaatissa kaikille.",
        default=True)
    hide_from_archive = models.BooleanField(
        u'Piilotus arkistosta',
        help_text=u'Piilotetaanko kilpailun tulokset arkistosta ? Tämä ylikirjoittaa eventin asetuksen.',
        default=False)

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = u"kilpailu"
        verbose_name_plural = u"kilpailut"


class CompetitionParticipation(models.Model):
    competition = models.ForeignKey(
        Competition,
        verbose_name=u'Kilpailu',
        help_text=u'Kilpailu johon osallistuttu')
    user = models.ForeignKey(
        User,
        verbose_name=u'Käyttäjä',
        help_text=u'Osallistuja')
    participant_name = models.CharField(
        u'Osallistujan nimi',
        help_text=u'Nimimerkki jolla haluat osallistua.',
        max_length=32,
        default=u'')
    score = models.FloatField(
        u'Pisteet',
        help_text=u'Kilpailijan saavuttamat pisteet',
        blank=True,
        default=0)
    disqualified = models.BooleanField(
        u'Diskattu',
        help_text=u"Suoritus on diskattu sääntörikon tai teknisten virheiden takia.",
        default=False)
    disqualified_reason = models.TextField(
        u'Diskauksen syy',
        blank=True)

    def get_formatted_score(self):
        return u'{} {}'.format(self.score, self.competition.score_type)

    def get_rank(self):
        # Get results
        rankby = '-score'
        if self.competition.score_sort == 1:
            rankby = 'score'
        results = CompetitionParticipation.objects.filter(competition_id=self.competition.id).order_by(rankby)
        
        # Find self
        rank = 1
        for p in results:
            if p.id == self.id:
                return rank
            else:
                rank += 1
        return rank

    def __unicode__(self):
        return u'{}, {}: {}'.format(self.competition.name, self.participant_name, self.score)

    class Meta:
        verbose_name = u"ilmoittautuminen"
        verbose_name_plural = u"ilmoittautumiset"
