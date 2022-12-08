from auditlog.registry import auditlog
from django.contrib.auth.models import User
from django.db import models

from Instanssi.kompomaatti.models import Event


class BlogEntry(models.Model):
    event = models.ForeignKey(Event, verbose_name="Tapahtuma", on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name="Käyttäjä", on_delete=models.SET_NULL, null=True)
    title = models.CharField("Otsikko", help_text="Lyhyt otsikko entrylle.", max_length=128)
    text = models.TextField("Teksti")
    date = models.DateTimeField("Aika")
    public = models.BooleanField(
        "Julkinen",
        help_text="Mikäli entry on julkinen, tulee se näkyviin sekä tapahtuman sivuille että RSS-syötteeseen.",
        default=False,
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "entry"
        verbose_name_plural = "entryt"


class BlogComment(models.Model):
    user = models.ForeignKey(User, verbose_name="Käyttäjä", on_delete=models.SET_NULL, null=True)
    entry = models.ForeignKey(BlogEntry, verbose_name="Entry", on_delete=models.CASCADE)
    title = models.CharField("Otsikko", help_text="Lyhyt otsikko kommentille.", max_length=128, blank=True)
    text = models.TextField("Kommentti", help_text="Kommenttiteksti.")
    date = models.DateTimeField("Aika")

    def __str__(self) -> str:
        return self.text[:20]

    class Meta:
        verbose_name = "kommentti"
        verbose_name_plural = "kommentit"


auditlog.register(BlogEntry)
