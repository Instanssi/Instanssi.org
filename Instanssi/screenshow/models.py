from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from Instanssi.kompomaatti.models import Event


class NPSong(models.Model):
    event = models.ForeignKey(Event, verbose_name="Tapahtuma", on_delete=models.PROTECT)
    title = models.CharField("Kappale", max_length=255, blank=True)
    artist = models.CharField("Artisti", max_length=255, blank=True)
    time = models.DateTimeField("Aikaleima")
    state = models.IntegerField("Tila", choices=((0, "Play"), (1, "Stop")))

    def __str__(self):
        if self.state == 0:
            return "[Play] {} - {}".format(self.title, self.artist)
        else:
            return "[Stop]"

    class Meta:
        verbose_name = "soitettava kappale"
        verbose_name_plural = "soitettavat kappaleet"


class ScreenConfig(models.Model):
    event = models.OneToOneField(Event, verbose_name="Tapahtuma", unique=True, on_delete=models.PROTECT)
    enable_videos = models.BooleanField(
        "Näytä videoita", help_text="Näytetäänkö esityksessä videoita playlistiltä.", default=True
    )
    enable_twitter = models.BooleanField(
        "Näytä twitterfeed",
        help_text="Näytetäänkö esityksessä twittersyötteen sisältävä slaidi.",
        default=True,
    )
    enable_irc = models.BooleanField(
        "Näytä IRC", help_text="Näytetäänkö esityksessä irc-lokin sisältävä slaidi.", default=True
    )
    video_interval = models.IntegerField(
        "Videoiden näyttöväli",
        help_text="Kuinka usein videoita näytetään? Arvo annetaan minuuteissa. 0 = Joka kierroksella.",
        default=5,
    )

    def __str__(self):
        return "Asetukset tapahtumalle {}".format(self.event.name)

    class Meta:
        verbose_name = "screenikonffi"
        verbose_name_plural = "screenikonffit"


class PlaylistVideo(models.Model):
    event = models.ForeignKey(Event, verbose_name="Tapahtuma", on_delete=models.PROTECT)
    name = models.CharField("Nimi", max_length=64, help_text="Videon nimi tai otsikko.")
    url = models.URLField("Osoite", help_text="Linkki Youtube-videoon.")
    index = models.IntegerField(
        "Järjestysindeksi",
        help_text="Indeksi toistolistan järjestelemiseen. Pienimmällä numerolla varustetut toistetaan ensimmäiseksi.",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "toistolistavideo"
        verbose_name_plural = "toistolistavideot"


class Sponsor(models.Model):
    event = models.ForeignKey(Event, verbose_name="Tapahtuma", on_delete=models.PROTECT)
    name = models.CharField("Nimi", max_length=64, help_text="Sponsorin nimi")
    logo = models.ImageField(
        "Kuva", upload_to="screen/sponsorlogos/", help_text="Sponsorin logo", blank=True
    )
    logo_scaled = ImageSpecField([ResizeToFit(800, 375, True)], source="logo", format="PNG")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "sponsori"
        verbose_name_plural = "sponsorit"

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
    event = models.ForeignKey(Event, verbose_name="Tapahtuma", on_delete=models.PROTECT)
    show_start = models.DateTimeField("Alkuaika", help_text="Viestin näyttäminen alkaa")
    show_end = models.DateTimeField("Loppuaika", help_text="Viestin näyttäminen päättyy")
    text = models.TextField("Viesti", help_text="Viestin leipäteksti. Katso ettei tästä tule liian pitkä.")

    def __str__(self):
        if len(self.text) > 32:
            return "{} ...".format(self.text[:32])
        else:
            return self.text

    class Meta:
        verbose_name = "viesti"
        verbose_name_plural = "viestit"


class IRCMessage(models.Model):
    event = models.ForeignKey(Event, verbose_name="Tapahtuma", on_delete=models.PROTECT)
    date = models.DateTimeField("Aika")
    nick = models.CharField("Nimimerkki", max_length=64)
    message = models.TextField("Viesti")

    def __str__(self):
        if len(self.message) > 32:
            return "{} ...".format(self.message[:32])
        else:
            return self.message

    class Meta:
        verbose_name = "irc-viesti"
        verbose_name_plural = "irc-viestit"
