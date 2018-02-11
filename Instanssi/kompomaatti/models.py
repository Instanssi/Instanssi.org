# -*- coding: utf-8 -*-

import os.path
from urllib.parse import urlparse, parse_qs

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from Instanssi.kompomaatti.misc import entrysort, sizeformat


class Profile(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Käyttäjä')
    otherinfo = models.TextField(
        'Muut yhteystiedot',
        help_text='Muita yhteystietoja, mm. IRC-tunnus (verkon kera), jne.')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "profiili"
        verbose_name_plural = "profiilit"


class Event(models.Model):
    name = models.CharField(
        'Nimi',
        max_length=64,
        help_text="Tapahtuman nimi",
        unique=True)
    date = models.DateField(
        'Päivämäärä',
        help_text="Tapahtuman päivämäärä (alku)")
    archived = models.BooleanField(
        'Arkistoitu',
        help_text="Saa näyttää arkistossa",
        default=False)
    mainurl = models.URLField(
        'Tapahtuman pääsivu', help_text='URL Tapahtuman pääsivustolle', blank=True)

    def __str__(self):
        return '[{}] {}'.format(self.pk, self.name)

    class Meta:
        verbose_name = "tapahtuma"
        verbose_name_plural = "tapahtumat"


class VoteCodeRequest(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name='Tapahtuma',
        help_text='Tapahtuma, johon äänestysoikeutta pyydetään',
        null=True)
    user = models.OneToOneField(
        User,
        verbose_name='Käyttäjä',
        help_text='Pyynnön esittänyt käyttäjä')
    text = models.TextField(
        'Kuvaus',
        help_text='Lyhyt aneluteksti admineille :)')

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = (("event", "user"), )
        verbose_name = "äänestyskoodipyyntö"
        verbose_name_plural = "äänestyskoodipyynnöt"


class TicketVoteCode(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name='Tapahtuma',
        help_text='Tapahtuma, johon äänestysavain on assosioitu',
        blank=True,
        null=True)
    associated_to = models.ForeignKey(
        User,
        verbose_name='Käyttäjä',
        help_text="Käyttäjä jolle avain on assosioitu",
        blank=True,
        null=True)
    ticket = models.ForeignKey(
        'store.TransactionItem',  # String to avoid circular dependency
        verbose_name='Lipputuote',
        help_text='Lipputuote jonka avainta käytetään äänestysavaimena',
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    time = models.DateTimeField(
        'Aikaleima',
        help_text="Aika jolloin avain assosioitiin käyttäjälle.",
        blank=True,
        null=True)

    @property
    def key(self):
        if self.ticket:
            return self.ticket.key
        return None

    @property
    def associated_username(self):
        if self.associated_to:
            return self.associated_to.username
        return None

    def __str__(self):
        return '{}: {}'.format(self.key, self.associated_username)

    class Meta:
        verbose_name = "lippuäänestusavain"
        verbose_name_plural = "lippuäänestysavaimet"
        unique_together = (("event", "ticket"), ("event", "associated_to"))


class VoteCode(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name='Tapahtuma',
        help_text='Tapahtuma, johon äänestysavain on assosioitu',
        blank=True,
        null=True)
    key = models.CharField(
        'Avain',
        help_text="Äänestysavain.",
        max_length=64,
        unique=True)
    associated_to = models.ForeignKey(
        User,
        verbose_name='Käyttäjä',
        help_text="Käyttäjä jolle avain on assosioitu",
        blank=True,
        null=True)
    time = models.DateTimeField(
        'Aikaleima',
        help_text="Aika jolloin avain assosioitiin käyttäjälle.",
        blank=True,
        null=True)

    def __str__(self):
        if self.associated_to:
            return '{}: {}'.format(self.key, self.associated_to.username)
        else:
            return str(self.key)

    class Meta:
        verbose_name = "äänestysavain"
        verbose_name_plural = "äänestysavaimet"
        unique_together = (("event", "key"), ("event", "associated_to"))


class Compo(models.Model):
    MAX_IMAGE_SIZE = 6 * 1024 * 1024

    ENTRY_VIEW_TYPES = (
        (0, 'Ei mitään'),
        (1, 'Youtube ensin, sitten kuva'),  # Videoentryille, koodauskompoille
        (2, 'Vain kuva'),  # Grafiikkakompoille
        (3, '(deprecated)'),
    )
    THUMBNAIL_REQ = (
        (0, 'Vaadi erillinen pikkukuva.'),
        (1, 'Käytä pikkukuvana teoksen tiedostoa (Toimii vain png/jpg-tiedostoille).'),
        (2, 'Salli pikkukuva (ei vaadittu).'),
        (3, 'Älä salli pikkukuvaa.'),
    )

    event = models.ForeignKey(
        Event,
        verbose_name="tapahtuma",
        help_text="Tapahtuma johon kompo kuuluu")
    name = models.CharField(
        'Nimi',
        max_length=32,
        help_text="Kompon nimi (max 32 merkkiä).")
    description = models.TextField(
        'Kuvaus')
    adding_end = models.DateTimeField(
        'Deadline entryjen lisäyksille',
        help_text="Tämän jälkeen kompoon ei voi enää lähettää uusia entryjä. Muokkaus toimii vielä.")
    editing_end = models.DateTimeField(
        'Deadline entryjen muokkauksille',
        help_text="Tämän jälkeen entryjen tiedostoja tai muita tietoja ei voi enää muokata.")
    compo_start = models.DateTimeField(
        'Kompon aloitusaika',
        help_text="Kompon alkamisaika tapahtumassa (tapahtumakalenteria varten).")
    voting_start = models.DateTimeField(
        'Äänestyksen alkamisaika',
        help_text="Alkamisaika entryjen äänestykselle.")
    voting_end = models.DateTimeField(
        'Äänestyksen päättymisaika',
        help_text='Päättymisaika entryjen äänestykselle.')
    entry_sizelimit = models.IntegerField(
        'Kokoraja entryille',
        help_text="Kokoraja entrytiedostoille (tavua).",
        default=134217728)  # Default to 128M
    source_sizelimit = models.IntegerField(
        'Kokoraja sorsille',
        help_text="Kokoraja sorsatiedostoille (tavua).",
        default=134217728)  # Default to 128M
    formats = models.CharField(
        'Sallitut tiedostopäätteet',
        max_length=128,
        help_text="Entrypaketille sallitut tiedostopäätteet pystyviivalla eroteltuna, esim. \"png|jpg\".",
        default="zip|7z|gz|bz2")
    source_formats = models.CharField(
        'Sallitut lähdekoodipaketin päätteet',
        max_length=128,
        help_text="Entryn lähdekoodipaketille sallitut tiedostopäätteet pystyviivalla eroteltuna",
        default="zip|7z|gz|bz2")
    image_formats = models.CharField(
        'Sallitut kuvatiedoston päätteet',
        max_length=128,
        help_text="Entryn pikkukuvalle sallitut tiedostopäätteet pystyviivalla eroteltuna",
        default="png|jpg")
    active = models.BooleanField(
        'Aktiivinen',
        help_text="Onko kompo aktiivinen, eli näytetäänkö se kompomaatissa kaikille.",
        default=True)
    show_voting_results = models.BooleanField(
        'Näytä tulokset',
        help_text="Näytä äänestustulokset.",
        default=False)
    entry_view_type = models.IntegerField(
        'Entryesittely',
        choices=ENTRY_VIEW_TYPES,
        default=0,
        help_text="Ilmoittaa millainen näkymä näytetään entryn tiedoissa. Latauslinkki näytetään aina.")
    hide_from_archive = models.BooleanField(
        'Piilotus arkistosta',
        help_text='Piilottaa kompon tulokset arkistosta. Tämä asetus ohittaa tapahtuman tiedoissa valitun asetuksen.',
        default=False)
    hide_from_frontpage = models.BooleanField(
        'Piilotus etusivulta',
        help_text='Piilottaa kompon nimen ja kuvauksen tapahtuman etusivulta. '
                  'Käytä esim. jos kompon kuvaus on vielä suunnitteilla.',
        default=False)
    is_votable = models.BooleanField(
        'Äänestettävissä',
        help_text='Teosta voi ylipäätään äänestää (Pois esim. robocodelle).',
        default=True)
    thumbnail_pref = models.IntegerField(
        'Pikkukuvan asetukset',
        choices=THUMBNAIL_REQ,
        default=2,
        help_text='Pikkukuvan luonti ja asettaminen.')
    
    def __str__(self):
        return self.event.name + ': ' + self.name
    
    class Meta:
        verbose_name = "kompo"
        verbose_name_plural = "kompot"
            
    def is_voting_open(self):
        if not self.is_votable:
            return False
        if self.voting_start <= timezone.now() < self.voting_end:
            return True
        return False
    
    def is_adding_open(self):
        if timezone.now() < self.adding_end:
            return True
        return False

    def is_editing_open(self):
        if timezone.now() < self.editing_end:
            return True
        return False

    def has_voting_started(self):
        if not self.is_votable:
            return False
        if timezone.now() > self.voting_start:
            return True
        return False

    @property
    def entry_format_list(self):
        return self.formats.split('|')

    @property
    def source_format_list(self):
        return self.source_formats.split('|')

    @property
    def image_format_list(self):
        return self.image_formats.split('|')

    @property
    def readable_entry_formats(self):
        return ', '.join(self.entry_format_list)

    @property
    def readable_source_formats(self):
        return ', '.join(self.source_format_list)

    @property
    def readable_image_formats(self):
        return ', '.join(self.image_format_list)

    @property
    def max_source_size(self):
        return self.source_sizelimit

    @property
    def max_entry_size(self):
        return self.entry_sizelimit

    @property
    def max_image_size(self):
        return self.MAX_IMAGE_SIZE

    @property
    def readable_max_source_size(self):
        return sizeformat.sizeformat(self.max_source_size)

    @property
    def readable_max_entry_size(self):
        return sizeformat.sizeformat(self.max_entry_size)

    @property
    def readable_max_image_size(self):
        return sizeformat.sizeformat(self.max_image_size)

    @property
    def is_imagefile_required(self):
        """ Is imagefile *required* for this compo """
        return self.thumbnail_pref == 0

    @property
    def is_imagefile_allowed(self):
        """ Is imagefile allowed for this compo """
        return self.thumbnail_pref in [0, 2]

    @property
    def is_imagefile_copied(self):
        """ Is imagefile copied from entryfile """
        return self.thumbnail_pref == 1


class Entry(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="käyttäjä",
        help_text="Käyttäjä jolle entry kuuluu")
    compo = models.ForeignKey(
        Compo,
        verbose_name="kompo",
        help_text="Kompo johon osallistutaan")
    name = models.CharField(
        'Nimi',
        max_length=64,
        help_text='Nimi tuotokselle')
    description = models.TextField(
        'Kuvaus',
        help_text='Voi sisältää mm. tietoja käytetyistä tekniikoista, muuta sanottavaa.')
    creator = models.CharField(
        'Tekijä',
        max_length=64,
        help_text='Tuotoksen tekijän tai tekijäryhmän nimi')
    entryfile = models.FileField(
        'Tiedosto',
        upload_to='kompomaatti/entryfiles/',
        help_text="Tuotospaketti.")
    sourcefile = models.FileField(
        'Lähdekoodi',
        upload_to='kompomaatti/entrysources/',
        help_text="Lähdekoodipaketti.",
        blank=True)
    imagefile_original = models.ImageField(
        'Kuva',
        upload_to='kompomaatti/entryimages/',
        help_text="Edustava kuva teokselle. Ei pakollinen, mutta suositeltava.",
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
        'Youtube URL',
        help_text="Linkki teoksen Youtube-videoon.",
        blank=True)
    disqualified = models.BooleanField(
        'Diskattu',
        help_text="Entry on diskattu sääntörikon tai teknisten ongelmien takia. "
                  "DISKAUS ON TEHTÄVÄ ENNEN ÄÄNESTYKSEN ALKUA!",
        default=False)
    disqualified_reason = models.TextField(
        'Syy diskaukseen',
        help_text="Diskauksen syy.",
        blank=True)
    archive_score = models.FloatField(
        'Pisteet',
        help_text='Arkistoidun entryn kompossa saamat pisteet. Mikäli tätä ei määritetä, '
                  'lasketaan pisteet suoraan äänestystuloksista.',
        null=True,
        blank=True)
    archive_rank = models.IntegerField(
        'Sijoitus',
        help_text='Arkistoidun entryn kompossa saama sijoitus. '
                  'Tämä voidaan laskea myös pistemääristä automaattisesti.',
        null=True,
        blank=True)

    def __str__(self):
        return '{} by {}'.format(self.name, self.creator)
    
    class Meta:
        verbose_name = "tuotos"
        verbose_name_plural = "tuotokset"
    
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

    @staticmethod
    def youtube_url_to_id(url):
        """Convert any valid YouTube URL to its video id."""
        # There's probably a regex that does this in one line...
        parsed = urlparse(url)
        querydict = parse_qs(parsed.query)
        if "v" in querydict:
            return querydict["v"][0]
        split_path = parsed.path.split("/")  # => ["", "v", "asdf"]
        if len(split_path) >= 2 and parsed.hostname == "youtu.be":
            return split_path[1]
        if len(split_path) >= 3 and split_path[1] == "v":
            return split_path[2]
        return None

    def get_youtube_embed_url(self):
        """Get embed URL for this entry's YouTube link."""
        video_id = self.youtube_url_to_id(self.youtube_url)
        return "//www.youtube.com/embed/{}/".format(video_id)
        
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
    user = models.ForeignKey(User, verbose_name="käyttäjä")
    compo = models.ForeignKey(Compo, verbose_name="kompo")
    entry = models.ForeignKey(Entry, verbose_name="tuotos")
    rank = models.IntegerField('Sijoitus')
    
    def __str__(self):
        return '{} by {} as {}'.format(self.entry.name, self.user.username, self.rank)
    
    class Meta:
        verbose_name = "ääni"
        verbose_name_plural = "äänet"


class Competition(models.Model):
    ENTRY_VIEW_TYPES = (
        (0, 'Korkein tulos ensin'),
        (1, 'Matalin tulos ensin'),
    )

    event = models.ForeignKey(
        Event,
        verbose_name="Tapahtuma",
        help_text="Tapahtuma johon kilpailu kuuluu")
    name = models.CharField(
        'Nimi',
        max_length=32,
        help_text="Kilpailun nimi (max 32 merkkiä).")
    description = models.TextField(
        'Kuvaus')
    participation_end = models.DateTimeField(
        'Deadline osallistumiselle.',
        help_text="Tämän jälkeen kilpailuun ei voi enää osallistua.")
    start = models.DateTimeField(
        'Kilpailun alku',
        help_text="Kilpailun aloitusaika.")
    end = models.DateTimeField(
        'Kilpailun loppu',
        help_text="Kilpailun päättymisaika.",
        null=True,
        blank=True)
    score_type = models.CharField(
        'Pisteiden tyyppi',
        max_length=8,
        help_text='Pisteiden tyyppi (km, m, sek, ...). Maksimipituus 8 merkkiä.')
    score_sort = models.IntegerField(
        'Pisteiden järjestely',
        choices=ENTRY_VIEW_TYPES,
        help_text='Onko suurimman vai pienimmän tuloksen saavuttanut voittaja?',
        default=0)
    show_results = models.BooleanField(
        'Näytä tulokset',
        help_text="Näytä kilpailun tulokset.",
        default=False)
    active = models.BooleanField(
        'Aktiivinen',
        help_text="Onko kilpailu aktiivinen, eli näytetäänkö se kompomaatissa kaikille.",
        default=True)
    hide_from_archive = models.BooleanField(
        'Piilotus arkistosta',
        help_text='Piilotetaanko kilpailun tulokset arkistosta ? Tämä ylikirjoittaa eventin asetuksen.',
        default=False)

    def __str__(self):
        return "{}: {}".format(self.event.name, self.name)
    
    class Meta:
        verbose_name = "kilpailu"
        verbose_name_plural = "kilpailut"


class CompetitionParticipation(models.Model):
    competition = models.ForeignKey(
        Competition,
        verbose_name='Kilpailu',
        help_text='Kilpailu johon osallistuttu')
    user = models.ForeignKey(
        User,
        verbose_name='Käyttäjä',
        help_text='Osallistuja')
    participant_name = models.CharField(
        'Osallistujan nimi',
        help_text='Nimimerkki jolla haluat osallistua.',
        max_length=32,
        default='')
    score = models.FloatField(
        'Pisteet',
        help_text='Kilpailijan saavuttamat pisteet',
        blank=True,
        default=0)
    disqualified = models.BooleanField(
        'Diskattu',
        help_text="Suoritus on diskattu sääntörikon tai teknisten virheiden takia.",
        default=False)
    disqualified_reason = models.TextField(
        'Diskauksen syy',
        blank=True)

    def get_formatted_score(self):
        return '{} {}'.format(self.score, self.competition.score_type)

    def get_rank(self):
        # Get results
        rank_by = '-score'
        if self.competition.score_sort == 1:
            rank_by = 'score'
        results = CompetitionParticipation.objects.filter(competition_id=self.competition.id).order_by(rank_by)
        
        # Find self
        rank = 1
        for p in results:
            if p.id == self.id:
                return rank
            else:
                rank += 1
        return rank

    def __str__(self):
        return '{}, {}: {}'.format(self.competition.name, self.participant_name, self.score)

    class Meta:
        verbose_name = "ilmoittautuminen"
        verbose_name_plural = "ilmoittautumiset"
